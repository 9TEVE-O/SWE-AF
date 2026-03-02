/** A single generated file with a path and content. */
export interface GeneratedFile {
  path: string;
  content: string;
}

/** The structured response from the AI model. */
export interface GeneratedOutput {
  files: GeneratedFile[];
  previewHtml?: string;
}

/** Validated generate request payload. */
export interface GenerateRequest {
  instruction: string;
  previousCode?: string;
}
