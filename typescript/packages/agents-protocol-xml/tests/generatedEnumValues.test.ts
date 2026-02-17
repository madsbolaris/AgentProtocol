/**
 * Auto-generated enum value tests.
 * Tests that all enum values serialize and deserialize correctly.
 */

import { describe, it, expect } from '@jest/globals';
import {
  ChatRole,
} from '../src/models';


describe('ChatRole Enum Tests', () => {

  it('should serialize and deserialize system correctly', () => {
    // Arrange: Get enum value
    const enumValue = ChatRole.System;

    // Act: Serialize to string
    const serialized = enumValue.toString();

    // Assert: Value serializes correctly
    expect(serialized).toBeDefined();
    expect(serialized.length).toBeGreaterThan(0);

    // Act: Parse back
    const parsed = ChatRole[serialized as keyof typeof ChatRole];

    // Assert: Round-trip successful
    expect(parsed).toBe(enumValue);
  });

  it('should serialize and deserialize developer correctly', () => {
    // Arrange: Get enum value
    const enumValue = ChatRole.Developer;

    // Act: Serialize to string
    const serialized = enumValue.toString();

    // Assert: Value serializes correctly
    expect(serialized).toBeDefined();
    expect(serialized.length).toBeGreaterThan(0);

    // Act: Parse back
    const parsed = ChatRole[serialized as keyof typeof ChatRole];

    // Assert: Round-trip successful
    expect(parsed).toBe(enumValue);
  });

  it('should serialize and deserialize agent correctly', () => {
    // Arrange: Get enum value
    const enumValue = ChatRole.Agent;

    // Act: Serialize to string
    const serialized = enumValue.toString();

    // Assert: Value serializes correctly
    expect(serialized).toBeDefined();
    expect(serialized.length).toBeGreaterThan(0);

    // Act: Parse back
    const parsed = ChatRole[serialized as keyof typeof ChatRole];

    // Assert: Round-trip successful
    expect(parsed).toBe(enumValue);
  });

  it('should serialize and deserialize user correctly', () => {
    // Arrange: Get enum value
    const enumValue = ChatRole.User;

    // Act: Serialize to string
    const serialized = enumValue.toString();

    // Assert: Value serializes correctly
    expect(serialized).toBeDefined();
    expect(serialized.length).toBeGreaterThan(0);

    // Act: Parse back
    const parsed = ChatRole[serialized as keyof typeof ChatRole];

    // Assert: Round-trip successful
    expect(parsed).toBe(enumValue);
  });

  it('should serialize and deserialize tool correctly', () => {
    // Arrange: Get enum value
    const enumValue = ChatRole.Tool;

    // Act: Serialize to string
    const serialized = enumValue.toString();

    // Assert: Value serializes correctly
    expect(serialized).toBeDefined();
    expect(serialized.length).toBeGreaterThan(0);

    // Act: Parse back
    const parsed = ChatRole[serialized as keyof typeof ChatRole];

    // Assert: Round-trip successful
    expect(parsed).toBe(enumValue);
  });

  it('should serialize and deserialize channel correctly', () => {
    // Arrange: Get enum value
    const enumValue = ChatRole.Channel;

    // Act: Serialize to string
    const serialized = enumValue.toString();

    // Assert: Value serializes correctly
    expect(serialized).toBeDefined();
    expect(serialized.length).toBeGreaterThan(0);

    // Act: Parse back
    const parsed = ChatRole[serialized as keyof typeof ChatRole];

    // Assert: Round-trip successful
    expect(parsed).toBe(enumValue);
  });

  it('should have all valid enum values', () => {
    // Arrange: Get all enum values
    const allValues = Object.values(ChatRole);

    // Assert: Each value can be serialized and deserialized
    allValues.forEach(value => {
      const serialized = value.toString();
      expect(serialized).toBeDefined();
      const parsed = ChatRole[serialized as keyof typeof ChatRole];
      expect(parsed).toBe(value);
    });
  });

});
