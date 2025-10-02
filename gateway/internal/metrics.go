package internal

// Placeholder for Prometheus metrics
// TODO: Implement prometheus/client_golang
// - Histogram for request duration
// - Counter for requests by status code
// - Gauge for active connections

type Metrics struct{}

func NewMetrics() *Metrics {
	return &Metrics{}
}

func (m *Metrics) RecordRequest(path string, statusCode int, duration float64) {
	// TODO: Prometheus histogram
}

func (m *Metrics) IncrementIngestCount() {
	// TODO: Prometheus counter
}