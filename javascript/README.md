# Microsoft Agents Protocol - JavaScript/TypeScript

This directory contains the JavaScript/TypeScript implementation of the Microsoft Agents Protocol.

## Packages

This is a monorepo containing the following packages:

### [@microsoft/agents-protocol-types](./packages/agents-protocol-types)
TypeScript type definitions generated from TypeSpec schemas. Provides strongly-typed interfaces for all protocol models.

### [@microsoft/agents-protocol-client](./packages/agents-protocol-client)
API client SDK for interacting with Agent Protocol-compliant services. Handles REST API calls, SSE streaming, and webhooks.

### [@microsoft/agents-react-ui](./packages/agents-react-ui)
React component library for building chat interfaces with Agent Protocol support. Includes components, hooks, and utilities.

## Getting Started

### Prerequisites
- Node.js >= 18.0.0
- npm >= 9.0.0

### Installation

```bash
# Install dependencies for all packages
npm install

# Build all packages
npm run build

# Run tests
npm run test

# Lint code
npm run lint

# Format code
npm run format
```

### Development

Each package can be developed independently:

```bash
# Work on protocol types
cd packages/agents-protocol-types
npm run dev

# Work on protocol client
cd packages/agents-protocol-client
npm run dev

# Work on React UI
cd packages/agents-react-ui
npm run dev
npm run storybook  # Launch Storybook
```

## Monorepo Structure

```
javascript/
├── packages/
│   ├── agents-protocol-types/    # TypeScript types (generated)
│   ├── agents-protocol-client/   # API client SDK
│   └── agents-react-ui/          # React components
├── package.json                  # Root package.json with workspaces
├── tsconfig.json                 # Shared TypeScript config
├── .eslintrc.js                  # Shared ESLint config
└── README.md                     # This file
```

## Scripts

- `npm run build` - Build all packages
- `npm run test` - Run tests for all packages
- `npm run lint` - Lint all packages
- `npm run format` - Format code with Prettier
- `npm run type-check` - Type check without emitting
- `npm run clean` - Clean build artifacts

## Code Generation

The `agents-protocol-types` package is generated from TypeSpec definitions in `../specs/typespec/`.

See [packages/agents-protocol-types/README.md](./packages/agents-protocol-types/README.md) for details on the code generation process.

## Contributing

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## License

[Your License Here]
