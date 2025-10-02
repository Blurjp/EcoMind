package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
	"github.com/go-redis/redis/v8"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/segmentio/kafka-go"
)

type Event struct {
	OrgID      string                 `json:"org_id"`
	UserID     string                 `json:"user_id"`
	Provider   string                 `json:"provider"`
	Model      string                 `json:"model"`
	TokensIn   int                    `json:"tokens_in"`
	TokensOut  int                    `json:"tokens_out"`
	NodeType   string                 `json:"node_type,omitempty"`
	Region     string                 `json:"region,omitempty"`
	Timestamp  string                 `json:"ts"`
	Source     string                 `json:"source,omitempty"`
	Metadata   map[string]interface{} `json:"metadata,omitempty"`
}

type Gateway struct {
	kafkaWriter *kafka.Writer
	redisClient *redis.Client
	logger      zerolog.Logger
}

func NewGateway(kafkaBrokers []string, redisAddr string) *Gateway {
	logger := log.Output(zerolog.ConsoleWriter{Out: os.Stderr})

	kafkaWriter := &kafka.Writer{
		Addr:         kafka.TCP(kafkaBrokers...),
		Topic:        "events.raw",
		Balancer:     &kafka.Hash{},
		RequiredAcks: kafka.RequireOne,
		Compression:  kafka.Snappy,
		BatchSize:    100,
		BatchTimeout: 10 * time.Millisecond,
	}

	redisClient := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})

	return &Gateway{
		kafkaWriter: kafkaWriter,
		redisClient: redisClient,
		logger:      logger,
	}
}

func (g *Gateway) HealthHandler(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	// Check Kafka
	kafkaOk := true
	conn, err := kafka.DialContext(ctx, "tcp", g.kafkaWriter.Addr.String())
	if err != nil {
		kafkaOk = false
	} else {
		conn.Close()
	}

	// Check Redis
	redisOk := g.redisClient.Ping(ctx).Err() == nil

	status := "healthy"
	httpStatus := http.StatusOK
	if !kafkaOk || !redisOk {
		status = "degraded"
		httpStatus = http.StatusServiceUnavailable
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(httpStatus)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": status,
		"kafka":  kafkaOk,
		"redis":  redisOk,
		"ts":     time.Now().UTC().Format(time.RFC3339),
	})
}

func (g *Gateway) IngestHandler(w http.ResponseWriter, r *http.Request) {
	var event Event
	if err := json.NewDecoder(r.Body).Decode(&event); err != nil {
		g.logger.Error().Err(err).Msg("invalid JSON")
		http.Error(w, "invalid JSON", http.StatusBadRequest)
		return
	}

	// Validate required fields
	if event.OrgID == "" || event.UserID == "" || event.Provider == "" {
		http.Error(w, "org_id, user_id, and provider are required", http.StatusBadRequest)
		return
	}

	// Set defaults
	if event.Timestamp == "" {
		event.Timestamp = time.Now().UTC().Format(time.RFC3339)
	}
	if event.Source == "" {
		event.Source = "gateway"
	}

	// Serialize and send to Kafka
	eventBytes, err := json.Marshal(event)
	if err != nil {
		g.logger.Error().Err(err).Msg("marshal error")
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}

	msg := kafka.Message{
		Key:   []byte(event.OrgID), // Partition by org_id
		Value: eventBytes,
		Time:  time.Now(),
	}

	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	if err := g.kafkaWriter.WriteMessages(ctx, msg); err != nil {
		g.logger.Error().Err(err).Msg("kafka write failed")
		http.Error(w, "failed to write event", http.StatusInternalServerError)
		return
	}

	g.logger.Info().
		Str("org_id", event.OrgID).
		Str("user_id", event.UserID).
		Str("provider", event.Provider).
		Msg("event ingested")

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "accepted",
		"ts":     time.Now().UTC().Format(time.RFC3339),
	})
}

func (g *Gateway) Close() error {
	if err := g.kafkaWriter.Close(); err != nil {
		return err
	}
	if err := g.redisClient.Close(); err != nil {
		return err
	}
	return nil
}

func main() {
	// Config from env
	port := getEnv("PORT", "8080")
	kafkaBrokers := getEnv("KAFKA_BROKERS", "localhost:9092")
	redisAddr := getEnv("REDIS_ADDR", "localhost:6379")

	gateway := NewGateway([]string{kafkaBrokers}, redisAddr)
	defer gateway.Close()

	// Router
	r := chi.NewRouter()
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(30 * time.Second))
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type"},
		AllowCredentials: false,
	}))

	r.Get("/health", gateway.HealthHandler)
	r.Post("/v1/ingest", gateway.IngestHandler)

	srv := &http.Server{
		Addr:         ":" + port,
		Handler:      r,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Graceful shutdown
	done := make(chan os.Signal, 1)
	signal.Notify(done, os.Interrupt, syscall.SIGTERM)

	go func() {
		log.Info().Str("port", port).Msg("gateway starting")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal().Err(err).Msg("server failed")
		}
	}()

	<-done
	log.Info().Msg("gateway shutting down")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal().Err(err).Msg("shutdown failed")
	}

	log.Info().Msg("gateway stopped")
}

func getEnv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}