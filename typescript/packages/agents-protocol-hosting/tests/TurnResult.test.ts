import { TurnResult } from '../src/core/TurnResult.js';

describe('TurnResult', () => {
  describe('enum values', () => {
    it('should have Continue value', () => {
      expect(TurnResult.Continue).toBe('continue');
    });

    it('should have Consumed value', () => {
      expect(TurnResult.Consumed).toBe('consumed');
    });

    it('should have Replied value', () => {
      expect(TurnResult.Replied).toBe('replied');
    });
  });

  describe('enum behavior', () => {
    it('should be able to compare enum values', () => {
      const result = TurnResult.Continue;
      expect(result === TurnResult.Continue).toBe(true);
      const result2 = TurnResult.Consumed;
      expect(result2 === TurnResult.Consumed).toBe(true);
    });

    it('should be able to switch on enum values', () => {
      const testSwitch = (result: TurnResult): string => {
        switch (result) {
          case TurnResult.Continue:
            return 'continue';
          case TurnResult.Consumed:
            return 'consumed';
          case TurnResult.Replied:
            return 'replied';
          default:
            return 'unknown';
        }
      };

      expect(testSwitch(TurnResult.Continue)).toBe('continue');
      expect(testSwitch(TurnResult.Consumed)).toBe('consumed');
      expect(testSwitch(TurnResult.Replied)).toBe('replied');
    });

    it('should support all enum values in an array', () => {
      const allResults = [TurnResult.Continue, TurnResult.Consumed, TurnResult.Replied];
      expect(allResults).toHaveLength(3);
      expect(allResults).toContain(TurnResult.Continue);
      expect(allResults).toContain(TurnResult.Consumed);
      expect(allResults).toContain(TurnResult.Replied);
    });
  });
});
