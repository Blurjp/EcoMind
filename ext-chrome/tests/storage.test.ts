import { StorageManager } from '../src/bg/storage';
import { DEFAULT_SETTINGS } from '../src/common/constants';

// Mock chrome.storage.local
const mockGet = jest.fn();
const mockSet = jest.fn();

(global as any).chrome = {
  storage: {
    local: {
      get: mockGet,
      set: mockSet,
    },
  },
  action: {
    setBadgeText: jest.fn(),
    setBadgeBackgroundColor: jest.fn(),
  },
};

describe('StorageManager', () => {
  let storageManager: StorageManager;

  beforeEach(() => {
    storageManager = StorageManager.getInstance();
    jest.clearAllMocks();
  });

  describe('getSettings', () => {
    it('should deep merge settings to prevent NaN values', async () => {
      // Simulate partial settings without estimationParams
      mockGet.mockResolvedValue({
        ecomind_settings: {
          baseUrl: 'https://api.example.com',
          userId: 'test-user',
          telemetryEnabled: true,
          // Missing estimationParams - this used to cause NaN
        },
      });

      const settings = await storageManager.getSettings();

      expect(settings.estimationParams.kwhPerCall).toBe(DEFAULT_SETTINGS.estimationParams.kwhPerCall);
      expect(settings.estimationParams.pue).toBe(DEFAULT_SETTINGS.estimationParams.pue);
      expect(settings.estimationParams.waterLPerKwh).toBe(DEFAULT_SETTINGS.estimationParams.waterLPerKwh);
      expect(settings.estimationParams.co2KgPerKwh).toBe(DEFAULT_SETTINGS.estimationParams.co2KgPerKwh);
    });

    it('should preserve partial estimationParams', async () => {
      mockGet.mockResolvedValue({
        ecomind_settings: {
          baseUrl: 'https://api.example.com',
          estimationParams: {
            kwhPerCall: 0.001, // Custom value
            // Missing other params - should get defaults
          },
        },
      });

      const settings = await storageManager.getSettings();

      expect(settings.estimationParams.kwhPerCall).toBe(0.001);
      expect(settings.estimationParams.pue).toBe(DEFAULT_SETTINGS.estimationParams.pue);
      expect(settings.estimationParams.waterLPerKwh).toBe(DEFAULT_SETTINGS.estimationParams.waterLPerKwh);
      expect(settings.estimationParams.co2KgPerKwh).toBe(DEFAULT_SETTINGS.estimationParams.co2KgPerKwh);
    });

    it('should handle empty storage', async () => {
      mockGet.mockResolvedValue({});

      const settings = await storageManager.getSettings();

      expect(settings).toEqual(DEFAULT_SETTINGS);
    });
  });
});