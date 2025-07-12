declare module 'incomplete-json-parser' {
  export class IncompleteJsonParser {
    constructor();
    write(chunk: string): void;
    getObjects(): any;
    reset(): void;
  }
}
