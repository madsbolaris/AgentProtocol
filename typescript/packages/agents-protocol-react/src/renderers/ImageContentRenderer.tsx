/**
 * Renderer for image content
 */

import React, { useState } from 'react';
import type { ImageContent } from '@microsoft/agents';
import { ContentRendererProps } from '../types';

export function ImageContentRenderer({ content }: ContentRendererProps<ImageContent>) {
  const imageContent = content as ImageContent;
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  if (hasError) {
    return (
      <div className="content-image-error">
        <span>🖼️ Image failed to load</span>
      </div>
    );
  }

  return (
    <div className="content-image">
      {!isLoaded && <div className="content-image-loading">Loading image...</div>}
      <img
        src={imageContent.uri}
        alt={imageContent.altText || 'Image'}
        className="content-image-img"
        onLoad={() => setIsLoaded(true)}
        onError={() => setHasError(true)}
        style={{ display: isLoaded ? 'block' : 'none' }}
      />
      {imageContent.altText && (
        <div className="content-image-caption">{imageContent.altText}</div>
      )}
    </div>
  );
}
