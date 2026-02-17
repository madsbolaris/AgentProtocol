import type { ChatMessage, AIContent } from '@microsoft/agents-protocol-abstractions';
import type { IValidator } from '../../core/IValidator';
import type { ValidationContext } from '../../core/ValidationContext';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Base class for all message validators.
 * Provides common validation logic for all message types.
 */
export abstract class MessageValidatorBase<T extends ChatMessage> implements IValidator<T> {
  public validate(message: T, context?: ValidationContext): ValidationResult {
    const errors: ValidationError[] = [];

    // Validate common fields
    errors.push(...this.validateCommonFields(message, context));

    // Validate message-specific fields
    errors.push(...this.validateSpecificFields(message, context));

    // Validate contents
    errors.push(...this.validateContents(message, context));

    return new ValidationResult(errors);
  }

  /**
   * Validates fields common to all message types.
   */
  protected validateCommonFields(message: T, context?: ValidationContext): ValidationError[] {
    const errors: ValidationError[] = [];

    // MSG-001: message-id must be non-empty
    if (!message.messageId || message.messageId.trim().length === 0) {
      errors.push(
        new ValidationError(
          ValidationErrorCode.MSG_001,
          'message-id must be non-empty',
          'messageId'
        )
      );
    }

    // MSG-002: message-id must be unique within thread (if context available)
    if (context && message.messageId) {
      if (!context.registerMessage(message)) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.MSG_002,
            `Duplicate message-id: ${message.messageId}`,
            'messageId'
          )
        );
      }
    }

    // MSG-004: created-at must not be in the future
    if (message.createdAt) {
      const now = new Date();
      const createdAt = new Date(message.createdAt);
      if (createdAt > now) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.MSG_004,
            'created-at must not be in the future',
            'createdAt'
          )
        );
      }
    }

    // MSG-005: author-name must not exceed 100 characters
    if (message.authorName && message.authorName.length > 100) {
      errors.push(
        new ValidationError(
          ValidationErrorCode.MSG_005,
          'author-name must not exceed 100 characters',
          'authorName'
        )
      );
    }

    // MSG-006: parent-message-id must reference existing message (if context available)
    if (context && message.parentMessageId) {
      if (!context.hasMessage(message.parentMessageId)) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.MSG_006,
            `parent-message-id references non-existent message: ${message.parentMessageId}`,
            'parentMessageId'
          )
        );
      }
    }

    return errors;
  }

  /**
   * Validates message-specific fields. Implemented by derived classes.
   */
  protected abstract validateSpecificFields(
    message: T,
    context?: ValidationContext
  ): ValidationError[];

  /**
   * Validates message contents. Can be overridden by derived classes.
   */
  protected validateContents(message: T, context?: ValidationContext): ValidationError[] {
    const errors: ValidationError[] = [];

    // MSG-010: Contents must not be empty (most message types)
    if (!message.contents || message.contents.length === 0) {
      // Only UserMessage, AgentMessage, ToolMessage, and ChannelMessage require contents
      // SystemMessage and DeveloperMessage can be empty
      const requiresContent = this.requiresContent();
      if (requiresContent) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.MSG_010,
            'Message must have at least one content item',
            'contents'
          )
        );
      }
    }

    // Validate allowed content types for this message role
    if (message.contents) {
      const allowedTypes = this.getAllowedContentTypes();
      for (const content of message.contents) {
        if (!this.isAllowedContentType(content, allowedTypes)) {
          errors.push(
            new ValidationError(
              this.getRoleSpecificErrorCode(),
              `${this.getMessageTypeName()} cannot contain ${content.kind} content`,
              'contents'
            )
          );
        }
      }
    }

    return errors;
  }

  /**
   * Returns whether this message type requires content.
   * Override in derived classes if needed.
   */
  protected requiresContent(): boolean {
    return true; // Most message types require content
  }

  /**
   * Returns the allowed content types for this message role.
   * Must be implemented by derived classes.
   */
  protected abstract getAllowedContentTypes(): string[];

  /**
   * Returns the role-specific error code for invalid content types.
   * Must be implemented by derived classes.
   */
  protected abstract getRoleSpecificErrorCode(): string;

  /**
   * Returns the message type name for error messages.
   * Must be implemented by derived classes.
   */
  protected abstract getMessageTypeName(): string;

  /**
   * Checks if a content type is allowed for this message role.
   */
  protected isAllowedContentType(content: AIContent, allowedTypes: string[]): boolean {
    return allowedTypes.includes(content.kind);
  }

  /**
   * Helper to validate that a field is non-empty.
   */
  protected validateNotEmpty(
    value: string | null | undefined,
    fieldName: string,
    errorCode: string,
    errorMessage: string
  ): ValidationError | undefined {
    if (!value || value.trim().length === 0) {
      return new ValidationError(errorCode, errorMessage, fieldName);
    }
    return undefined;
  }

  /**
   * Helper to collect non-null validation errors.
   */
  protected collectErrors(...errors: (ValidationError | undefined)[]): ValidationError[] {
    return errors.filter((e): e is ValidationError => e !== undefined);
  }
}
