/**
 * Agent Runtime API - TypeSpec Entry Point
 *
 * This is the main entry point for TypeSpec compilation.
 * It imports all API definition files and configures the service.
 */

import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "@typespec/versioning";

// Import all API definition files
import "./common.tsp";
import "./conditions.tsp";
import "./messages.tsp";
import "./usage.tsp";
import "./tools.tsp";
import "./agents.tsp";
import "./hooks.tsp";
import "./execution.tsp";
import "./subscriptions.tsp";
import "./streaming.tsp";
import "./routes.tsp";
import "./eval.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;

@service({
  title: "Agent Runtime API",
})
@server("https://api.example.com", "Agent Runtime API endpoint")
namespace Microsoft.Agents.AI;
