// Jest setup file for Ecomind extension tests

// Mock chrome APIs
global.chrome = {
  storage: {
    local: {
      get: jest.fn(),
      set: jest.fn(),
      clear: jest.fn(),
    },
  },
  runtime: {
    sendMessage: jest.fn(),
    onMessage: {
      addListener: jest.fn(),
    },
    lastError: null,
  },
  alarms: {
    create: jest.fn(),
    clear: jest.fn(),
    onAlarm: {
      addListener: jest.fn(),
    },
  },
  action: {
    setBadgeText: jest.fn(),
    setBadgeBackgroundColor: jest.fn(),
  },
  webRequest: {
    onBeforeRequest: {
      addListener: jest.fn(),
    },
  },
} as any;

// Mock console methods in tests
global.console = {
  ...console,
  warn: jest.fn(),
  error: jest.fn(),
};