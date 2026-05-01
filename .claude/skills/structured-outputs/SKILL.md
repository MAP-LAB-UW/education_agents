---
name: structured-outputs
description: |
  Describes how to use structrued outputs with openai, anthropic, and gemini APIs

  Use when: making calls to openai, anthropic, and gemini APIs and the task requires structured outputs
user-invocable: true
---

# OpenAI API
# Structured model outputs

export const snippetRefusalsChatCompletionsApi = {
  python: `
class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
steps: list[Step]
final_answer: str

completion = client.chat.completions.parse(
model="gpt-4o-2024-08-06",
messages=[
{"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
{"role": "user", "content": "how can I solve 8x + 7 = -23"},
],
response_format=MathReasoning,
)

math_reasoning = completion.choices[0].message

# If the model refuses to respond, you will get a refusal message

if math_reasoning.refusal:
print(math_reasoning.refusal)
else:
print(math_reasoning.parsed)
`.trim(),
  "javascript": `
const Step = z.object({
explanation: z.string(),
output: z.string(),
});

const MathReasoning = z.object({
steps: z.array(Step),
final_answer: z.string(),
});

const completion = await openai.chat.completions.parse({
model: "gpt-4o-2024-08-06",
messages: [
{ role: "system", content: "You are a helpful math tutor. Guide the user through the solution step by step." },
{ role: "user", content: "how can I solve 8x + 7 = -23" },
],
response_format: zodResponseFormat(MathReasoning, "math_reasoning"),
});

const math_reasoning = completion.choices[0].message

// If the model refuses to respond, you will get a refusal message
if (math_reasoning.refusal) {
console.log(math_reasoning.refusal);
} else {
console.log(math_reasoning.parsed);
}
`.trim(),
};
export const snippetRefusalsResponsesApi = {
  python: `
class Step(BaseModel):
explanation: str
output: str

class MathReasoning(BaseModel):
steps: list[Step]
final_answer: str

response = client.responses.parse(
model="gpt-4o-2024-08-06",
input=[
{"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
{"role": "user", "content": "how can I solve 8x + 7 = -23"},
],
text_format=MathReasoning,
)

for output in response.output:
if output.type != "message":
raise Exception("Unexpected non message")

    for item in output.content:
        if item.type == "refusal":
            # If the model refuses to respond, you will get a refusal message
            print(item.refusal)
            continue

        if not item.parsed:
            raise Exception("Could not parse response")

        print(item.parsed)

`.trim(),
  "javascript": `
const Step = z.object({
explanation: z.string(),
output: z.string(),
});

const MathReasoning = z.object({
steps: z.array(Step),
final_answer: z.string(),
});

const response = await openai.responses.parse({
model: "gpt-4o-2024-08-06",
input: [
{ role: "system", content: "You are a helpful math tutor. Guide the user through the solution step by step." },
{ role: "user", content: "how can I solve 8x + 7 = -23" }
],
text: {
format: zodTextFormat(MathReasoning, "math_response"),
},
});

for (const output of response.output) {
if (output.type != "message") {
throw new Error("Unexpected non message");
}

    for (const item of output.content) {
        if (item.type == "refusal") {
            // If the model refuses to respond, you will get a refusal message
            console.log(item.refusal);
            continue;
        }

        if (!item.parsed) {
            throw new Error("Could not parse response");
        }

        console.log(item.parsed);
    }

}
`.trim(),
};

export const snippetRefusalApiResponseChatCompletionsApi = {
  json: `
{
  "id": "chatcmpl-9nYAG9LPNonX8DAyrkwYfemr3C8HC",
  "object": "chat.completion",
  "created": 1721596428,
  "model": "gpt-4o-2024-08-06",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        // highlight-start
        "refusal": "I'm sorry, I cannot assist with that request."
        // highlight-end
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 81,
    "completion_tokens": 11,
    "total_tokens": 92,
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  },
  "system_fingerprint": "fp_3407719c7f"
}
  `.trim(),
};
export const snippetRefusalApiResponseResponsesApi = {
  json: `
{
  "id": "resp_1234567890",
  "object": "response",
  "created_at": 1721596428,
  "status": "completed",
  "completed_at": 1721596429,
  "error": null,
  "incomplete_details": null,
  "input": [],
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [{
    "id": "msg_1234567890",
    "type": "message",
    "role": "assistant",
    "content": [
      // highlight-start
      {
        "type": "refusal",
        "refusal": "I'm sorry, I cannot assist with that request."
      }
      // highlight-end
    ]
  }],
  "usage": {
    "input_tokens": 81,
    "output_tokens": 11,
    "total_tokens": 92,
    "output_tokens_details": {
      "reasoning_tokens": 0,
    }
  },
}
  `.trim(),
};

JSON is one of the most widely used formats in the world for applications to exchange data.

Structured Outputs is a feature that ensures the model will always generate responses that adhere to your supplied [JSON Schema](https://json-schema.org/overview/what-is-jsonschema), so you don't need to worry about the model omitting a required key, or hallucinating an invalid enum value.

Some benefits of Structured Outputs include:

1. **Reliable type-safety:** No need to validate or retry incorrectly formatted responses
1. **Explicit refusals:** Safety-based model refusals are now programmatically detectable
1. **Simpler prompting:** No need for strongly worded prompts to achieve consistent formatting

In addition to supporting JSON Schema in the REST API, the OpenAI SDKs for [Python](https://github.com/openai/openai-python/blob/main/helpers.md#structured-outputs-parsing-helpers) and [JavaScript](https://github.com/openai/openai-node/blob/master/helpers.md#structured-outputs-parsing-helpers) also make it easy to define object schemas using [Pydantic](https://docs.pydantic.dev/latest/) and [Zod](https://zod.dev/) respectively. Below, you can see how to extract information from unstructured text that conforms to a schema defined in code.

### Supported models

Structured Outputs is available in our [latest large language models](https://developers.openai.com/api/docs/models), starting with GPT-4o. Older models like `gpt-4-turbo` and earlier may use [JSON mode](#json-mode) instead.




  

When to use Structured Outputs via function calling vs via{" "}
    <span className="monospace">text.format</span>




Structured Outputs is available in two forms in the OpenAI API:

1. When using [function calling](https://developers.openai.com/api/docs/guides/function-calling)
2. When using a `json_schema` response format

Function calling is useful when you are building an application that bridges the models and functionality of your application.

For example, you can give the model access to functions that query a database in order to build an AI assistant that can help users with their orders, or functions that can interact with the UI.

Conversely, Structured Outputs via `response_format` are more suitable when you want to indicate a structured schema for use when the model responds to the user, rather than when the model calls a tool.

For example, if you are building a math tutoring application, you might want the assistant to respond to your user using a specific JSON Schema so that you can generate a UI that displays different parts of the model's output in distinct ways.

Put simply:




  - If you are connecting the model to tools, functions, data, etc. in your
  system, then you should use function calling - If you want to structure the
  model's output when it responds to the user, then you should use a structured
  `text.format`





  The remainder of this guide will focus on non-function calling use cases in
    the Responses API. To learn more about how to use Structured Outputs with
    function calling, check out the{" "}
    [Function Calling](https://developers.openai.com/api/docs/guides/function-calling#function-calling-with-structured-outputs){" "}
    guide.


### Structured Outputs vs JSON mode

Structured Outputs is the evolution of [JSON mode](#json-mode). While both ensure valid JSON is produced, only Structured Outputs ensure schema adherence. Both Structured Outputs and JSON mode are supported in the Responses API, Chat Completions API, Assistants API, Fine-tuning API and Batch API.

We recommend always using Structured Outputs instead of JSON mode when possible.

However, Structured Outputs with `response_format: {type: "json_schema", ...}` is only supported with the `gpt-4o-mini`, `gpt-4o-mini-2024-07-18`, and `gpt-4o-2024-08-06` model snapshots and later.




|                                            | Structured Outputs                                                                                                             | JSON Mode                                  |
|--------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| **Outputs valid JSON**                     | Yes                                                                                                                            | Yes                                        |
| **Adheres to schema**                      | Yes (see [supported schemas](#supported-schemas))                                               | No                                         |
| **Compatible models**                      | `gpt-4o-mini`, `gpt-4o-2024-08-06`, and later                                                                                  | `gpt-3.5-turbo`, `gpt-4-*` and `gpt-4o-*` models |
| **Enabling**                               | `text: { format: { type: "json_schema", "strict": true, "schema": ... } }`                                       | `text: { format: { type: "json_object" } }` |


## Examples



<div data-content-switcher-pane data-value="chain-of-thought">
    <div class="hidden">Chain of thought</div>
    </div>
  <div data-content-switcher-pane data-value="structured-data" hidden>
    <div class="hidden">Structured data extraction</div>
    </div>
  <div data-content-switcher-pane data-value="ui-generation" hidden>
    <div class="hidden">UI generation</div>
    </div>
  <div data-content-switcher-pane data-value="moderation" hidden>
    <div class="hidden">Moderation</div>
    </div>








How to use Structured Outputs with <span className="monospace">text.format</span>


Refusals with Structured Outputs



When using Structured Outputs with user-generated input, OpenAI models may occasionally refuse to fulfill the request for safety reasons. Since a refusal does not necessarily follow the schema you have supplied in `response_format`, the API response will include a new field called `refusal` to indicate that the model refused to fulfill the request.

When the `refusal` property appears in your output object, you might present the refusal in your UI, or include conditional logic in code that consumes the response to handle the case of a refused request.

The API response from a refusal will look something like this:




  Tips and best practices



#### Handling user-generated input

If your application is using user-generated input, make sure your prompt includes instructions on how to handle situations where the input cannot result in a valid response.

The model will always try to adhere to the provided schema, which can result in hallucinations if the input is completely unrelated to the schema.

You could include language in your prompt to specify that you want to return empty parameters, or a specific sentence, if the model detects that the input is incompatible with the task.

#### Handling mistakes

Structured Outputs can still contain mistakes. If you see mistakes, try adjusting your instructions, providing examples in the system instructions, or splitting tasks into simpler subtasks. Refer to the [prompt engineering guide](https://developers.openai.com/api/docs/guides/prompt-engineering) for more guidance on how to tweak your inputs.

#### Avoid JSON schema divergence

To prevent your JSON Schema and corresponding types in your programming language from diverging, we strongly recommend using the native Pydantic/zod sdk support.

If you prefer to specify the JSON schema directly, you could add CI rules that flag when either the JSON schema or underlying data objects are edited, or add a CI step that auto-generates the JSON Schema from type definitions (or vice-versa).

## Streaming

## Supported schemas

## JSON mode

JSON mode is a more basic version of the Structured Outputs feature. While
  JSON mode ensures that model output is valid JSON, Structured Outputs reliably
  matches the model's output to the schema you specify. We recommend you use
  Structured Outputs if it is supported for your use case.

When JSON mode is turned on, the model's output is ensured to be valid JSON, except for in some edge cases that you should detect and handle appropriately.




To turn on JSON mode with the Responses API you can set the `text.format` to `{ "type": "json_object" }`. If you are using function calling, JSON mode is always turned on.


Important notes:

- When using JSON mode, you must always instruct the model to produce JSON via some message in the conversation, for example via your system message. If you don't include an explicit instruction to generate JSON, the model may generate an unending stream of whitespace and the request may run continually until it reaches the token limit. To help ensure you don't forget, the API will throw an error if the string "JSON" does not appear somewhere in the context.
- JSON mode will not guarantee the output matches any specific schema, only that it is valid and parses without errors. You should use Structured Outputs to ensure it matches your schema, or if that is not possible, you should use a validation library and potentially retries to ensure that the output matches your desired schema.
- Your application must detect and handle the edge cases that can result in the model output not being a complete JSON object (see below)

Handling edge cases

## Resources

To learn more about Structured Outputs, we recommend browsing the following resources:

- Check out our [introductory cookbook](https://developers.openai.com/cookbook/examples/structured_outputs_intro) on Structured Outputs
- Learn [how to build multi-agent systems](https://developers.openai.com/cookbook/examples/structured_outputs_multi_agent) with Structured Outputs

---

# Anthropic API
# Structured outputs

Get validated JSON results from agent workflows

---

Structured outputs constrain Claude's responses to follow a specific schema, ensuring valid, parseable output for downstream processing. Two complementary features are available:

- **JSON outputs** (`output_config.format`): Get Claude's response in a specific JSON format
- **Strict tool use** (`strict: true`): Guarantee schema validation on tool names and inputs

These features can be used independently or together in the same request.

<Note>
Structured outputs are generally available on the Claude API and Amazon Bedrock for Claude Opus 4.6, Claude Sonnet 4.6, Claude Sonnet 4.5, Claude Opus 4.5, and Claude Haiku 4.5. Structured outputs are in public beta on Microsoft Foundry.
</Note>

<Note>
Prompts and responses using structured outputs are processed with [Zero Data Retention (ZDR)](/docs/en/build-with-claude/zero-data-retention). However, the JSON schema itself is temporarily cached for up to 24 hours for optimization purposes. No prompt or response data is retained.
</Note>

<Tip>
**Migrating from beta?** The `output_format` parameter has moved to `output_config.format`, and beta headers are no longer required. The old beta header (`structured-outputs-2025-11-13`) and `output_format` parameter will continue working for a transition period. See code examples below for the updated API shape.
</Tip>

## Why use structured outputs

Without structured outputs, Claude can generate malformed JSON responses or invalid tool inputs that break your applications. Even with careful prompting, you may encounter:
- Parsing errors from invalid JSON syntax
- Missing required fields
- Inconsistent data types
- Schema violations requiring error handling and retries

Structured outputs guarantee schema-compliant responses through constrained decoding:
- **Always valid**: No more `JSON.parse()` errors
- **Type safe**: Guaranteed field types and required fields
- **Reliable**: No retries needed for schema violations

## JSON outputs

JSON outputs control Claude's response format, ensuring Claude returns valid JSON matching your schema. Use JSON outputs when you need to:

- Control Claude's response format
- Extract data from images or text
- Generate structured reports
- Format API responses

### Quick start

<CodeGroup>

```bash Shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
      }
    ],
    "output_config": {
      "format": {
        "type": "json_schema",
        "schema": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "plan_interest": {"type": "string"},
            "demo_requested": {"type": "boolean"}
          },
          "required": ["name", "email", "plan_interest", "demo_requested"],
          "additionalProperties": false
        }
      }
    }
  }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.",
        }
    ],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "plan_interest": {"type": "string"},
                    "demo_requested": {"type": "boolean"},
                },
                "required": ["name", "email", "plan_interest", "demo_requested"],
                "additionalProperties": False,
            },
        }
    },
)
print(response.content[0].text)
```

```typescript TypeScript hidelines={1..2}
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content:
        "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
    }
  ],
  output_config: {
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          name: { type: "string" },
          email: { type: "string" },
          plan_interest: { type: "string" },
          demo_requested: { type: "boolean" }
        },
        required: ["name", "email", "plan_interest", "demo_requested"],
        additionalProperties: false
      }
    }
  }
});
const textBlock = response.content.find((block) => block.type === "text");
if (textBlock && textBlock.type === "text") {
  console.log(textBlock.text);
}
```

```csharp C#
using System.Collections.Generic;
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

AnthropicClient client = new();

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 1024,
    Messages = [new() { Role = Role.User, Content = "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan." }],
    OutputConfig = new OutputConfig
    {
        Format = new JsonOutputFormat
        {
            Schema = new Dictionary<string, JsonElement>
            {
                ["type"] = JsonSerializer.SerializeToElement("object"),
                ["properties"] = JsonSerializer.SerializeToElement(new
                {
                    name = new { type = "string" },
                    email = new { type = "string" },
                    plan_interest = new { type = "string" },
                    demo_requested = new { type = "boolean" },
                }),
                ["required"] = JsonSerializer.SerializeToElement(new[] { "name", "email", "plan_interest", "demo_requested" }),
                ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
            },
        },
    },
};

var message = await client.Messages.Create(parameters);
Console.WriteLine(message);
```

```go Go hidelines={1..12,-3..-1}
package main

import (
	"context"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
)

func main() {
	client := anthropic.NewClient()

	response, _ := client.Messages.New(context.Background(),
		anthropic.MessageNewParams{
			Model:     anthropic.ModelClaudeOpus4_6,
			MaxTokens: 1024,
			Messages: []anthropic.MessageParam{
				anthropic.NewUserMessage(
					anthropic.NewTextBlock("Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan."),
				),
			},
			OutputConfig: anthropic.OutputConfigParam{
				Format: anthropic.JSONOutputFormatParam{
					Schema: map[string]interface{}{
						"type": "object",
						"properties": map[string]interface{}{
							"name":           map[string]string{"type": "string"},
							"email":          map[string]string{"type": "string"},
							"plan_interest":  map[string]string{"type": "string"},
							"demo_requested": map[string]string{"type": "boolean"},
						},
						"required":             []string{"name", "email", "plan_interest", "demo_requested"},
						"additionalProperties": false,
					},
				},
			},
		})

	fmt.Println(response.Content[0].Text)
}
```

```java Java hidelines={1..6}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.StructuredMessage;
import com.anthropic.models.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;

class ContactInfo {
    public String name;
    public String email;
    public String plan_interest;
    public boolean demo_requested;
}

public class StructuredOutputQuickStart {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        StructuredMessageCreateParams<ContactInfo> params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(1024)
            .addUserMessage("Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan.")
            .outputConfig(ContactInfo.class)
            .build();

        StructuredMessage<ContactInfo> response = client.messages().create(params);
        ContactInfo contact = response.content().get(0).asText().text();
        System.out.println(contact.name + " (" + contact.email + ")");
    }
}
```

```php PHP
<?php

use Anthropic\Client;

$client = new Client(
    apiKey: getenv("ANTHROPIC_API_KEY")
);

$response = $client->messages->create(
    maxTokens: 1024,
    messages: [
        [
            'role' => 'user',
            'content' => 'Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan.'
        ]
    ],
    model: 'claude-opus-4-6',
    outputConfig: [
        'format' => [
            'type' => 'json_schema',
            'schema' => [
                'type' => 'object',
                'properties' => [
                    'name' => ['type' => 'string'],
                    'email' => ['type' => 'string'],
                    'plan_interest' => ['type' => 'string'],
                    'demo_requested' => ['type' => 'boolean']
                ],
                'required' => ['name', 'email', 'plan_interest', 'demo_requested'],
                'additionalProperties' => false
            ]
        ]
    ],
);

echo $response->content[0]->text;
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

response = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan."
    }
  ],
  output_config: {
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          name: { type: "string" },
          email: { type: "string" },
          plan_interest: { type: "string" },
          demo_requested: { type: "boolean" }
        },
        required: ["name", "email", "plan_interest", "demo_requested"],
        additionalProperties: false
      }
    }
  }
)

puts response.content[0].text
```

</CodeGroup>

**Response format:** Valid JSON matching your schema in `response.content[0].text`

```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "plan_interest": "Enterprise",
  "demo_requested": true
}
```

### How it works

<Steps>
  <Step title="Define your JSON schema">
    Create a JSON schema that describes the structure you want Claude to follow. The schema uses standard JSON Schema format with some limitations (see [JSON Schema limitations](#json-schema-limitations)).
  </Step>
  <Step title="Add the output_config.format parameter">
    Include the `output_config.format` parameter in your API request with `type: "json_schema"` and your schema definition.
  </Step>
  <Step title="Parse the response">
    Claude's response is valid JSON matching your schema, returned in `response.content[0].text`.
  </Step>
</Steps>

### Working with JSON outputs in SDKs

The SDKs provide helpers that make it easier to work with JSON outputs, including schema transformation, automatic validation, and integration with popular schema libraries.

<Note>
SDK helper methods (like `.parse()` and Pydantic/Zod integration) still accept `output_format` as a convenience parameter. The SDK handles the translation to `output_config.format` internally. The examples below show the SDK helper syntax.
</Note>

#### Using native schema definitions

Instead of writing raw JSON schemas, you can use familiar schema definition tools in your language:

- **Python**: [Pydantic](https://docs.pydantic.dev/) models with `client.messages.parse()`
- **TypeScript**: [Zod](https://zod.dev/) schemas with `zodOutputFormat()`
- **Java**: Plain Java classes with automatic schema derivation via `outputConfig(Class<T>)`
- **Ruby**: `Anthropic::BaseModel` classes with `output_config: {format: Model}`
- **C#**, **Go**, **PHP**: Raw JSON schemas passed via `output_config`

<CodeGroup>

```python Python
from pydantic import BaseModel
from anthropic import Anthropic


class ContactInfo(BaseModel):
    name: str
    email: str
    plan_interest: str
    demo_requested: bool


client = Anthropic()

response = client.messages.parse(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.",
        }
    ],
    output_format=ContactInfo,
)

print(response.parsed_output)
```

```typescript TypeScript hidelines={1}
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const ContactInfoSchema = z.object({
  name: z.string(),
  email: z.string(),
  plan_interest: z.string(),
  demo_requested: z.boolean()
});

const client = new Anthropic();

const response = await client.messages.parse({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content:
        "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
    }
  ],
  output_config: { format: zodOutputFormat(ContactInfoSchema) }
});

// Automatically parsed and validated
console.log(response.parsed_output);
```

```csharp C#
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

var client = new AnthropicClient();

var response = await client.Messages.Create(new MessageCreateParams
{
    Model = "claude-opus-4-6",
    MaxTokens = 1024,
    Messages = [new() {
        Role = Role.User,
        Content = "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
    }],
    OutputConfig = new OutputConfig
    {
        Format = new JsonOutputFormat
        {
            Schema = new Dictionary<string, JsonElement>
            {
                ["type"] = JsonSerializer.SerializeToElement("object"),
                ["properties"] = JsonSerializer.SerializeToElement(new
                {
                    name = new { type = "string" },
                    email = new { type = "string" },
                    plan_interest = new { type = "string" },
                    demo_requested = new { type = "boolean" },
                }),
                ["required"] = JsonSerializer.SerializeToElement(
                    new[] { "name", "email", "plan_interest", "demo_requested" }),
                ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
            },
        },
    },
});

var json = (response.Content.First().Value as TextBlock)!.Text;
// JSON is guaranteed to match the schema
var contact = JsonSerializer.Deserialize<Dictionary<string, object>>(json);
Console.WriteLine($"{contact["name"]} ({contact["email"]})");
```

```go Go hidelines={1..2,4..7,28..29,-1}
package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/invopop/jsonschema"
)

type ContactInfo struct {
	Name          string `json:"name" jsonschema:"description=Full name"`
	Email         string `json:"email" jsonschema:"description=Email address"`
	PlanInterest  string `json:"plan_interest" jsonschema:"description=Plan type"`
	DemoRequested bool   `json:"demo_requested" jsonschema:"description=Whether a demo was requested"`
}

func generateSchema(v any) map[string]any {
	r := jsonschema.Reflector{AllowAdditionalProperties: false, DoNotReference: true}
	s := r.Reflect(v)
	b, _ := json.Marshal(s)
	var m map[string]any
	json.Unmarshal(b, &m)
	return m
}

func main() {
	client := anthropic.NewClient()
	schema := generateSchema(&ContactInfo{})

	message, _ := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock(
				"Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.",
			)),
		},
		OutputConfig: anthropic.OutputConfigParam{
			Format: anthropic.JSONOutputFormatParam{
				Schema: schema,
			},
		},
	})

	for _, block := range message.Content {
		switch variant := block.AsAny().(type) {
		case anthropic.TextBlock:
			var contact ContactInfo
			json.Unmarshal([]byte(variant.Text), &contact)
			fmt.Printf("%s (%s)\n", contact.Name, contact.Email)
		}
	}
}
```

```java Java hidelines={1..6,15..16,-1}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.StructuredMessage;
import com.anthropic.models.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;

class ContactInfo {
    public String name;
    public String email;
    public String planInterest;
    public boolean demoRequested;
}

public class NativeSchemaExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        StructuredMessageCreateParams<ContactInfo> createParams = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(1024)
            .outputConfig(ContactInfo.class)
            .addUserMessage("Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.")
            .build();

        StructuredMessage<ContactInfo> response = client.messages().create(createParams);
        ContactInfo contact = response.content().get(0).asText().text();
        System.out.println(contact.name + " (" + contact.email + ")");
    }
}
```

```php PHP hidelines={1..8}
<?php

use Anthropic\Client;
use Anthropic\Messages\OutputConfig;
use Anthropic\Messages\JSONOutputFormat;

$client = new Client();

$response = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => 'Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.'],
    ],
    model: 'claude-opus-4-6',
    outputConfig: OutputConfig::with(format: JSONOutputFormat::with(schema: [
        'type' => 'object',
        'properties' => [
            'name' => ['type' => 'string'],
            'email' => ['type' => 'string'],
            'plan_interest' => ['type' => 'string'],
            'demo_requested' => ['type' => 'boolean'],
        ],
        'required' => ['name', 'email', 'plan_interest', 'demo_requested'],
        'additionalProperties' => false,
    ])),
);

$data = json_decode($response->content[0]->text, true);
echo $data['name'] . ' (' . $data['email'] . ')';
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

class ContactInfo < Anthropic::BaseModel
  required :name, String
  required :email, String
  required :plan_interest, String
  required :demo_requested, Anthropic::Boolean
end

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
  }],
  output_config: {format: ContactInfo}
)

contact = message.parsed_output
puts "#{contact.name} (#{contact.email})"
```

</CodeGroup>

#### SDK-specific methods

Each SDK provides helpers that make working with structured outputs easier. See individual SDK pages for full details.

<Tabs>
<Tab title="Python">

**`client.messages.parse()` (Recommended)**

The `parse()` method automatically transforms your Pydantic model, validates the response, and returns a `parsed_output` attribute.

<section title="Example usage">

```python hidelines={2,11}
from pydantic import BaseModel
import anthropic


class ContactInfo(BaseModel):
    name: str
    email: str
    plan_interest: str


client = anthropic.Anthropic()

response = client.messages.parse(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Extract contact info: John Smith, john@example.com, interested in the Pro plan",
        }
    ],
    output_format=ContactInfo,
)

# Access the parsed output directly
contact = response.parsed_output
print(contact.name, contact.email)
```

</section>

**`transform_schema()` helper**

For when you need to manually transform schemas before sending, or when you want to modify a Pydantic-generated schema. Unlike `client.messages.parse()`, which transforms provided schemas automatically, this gives you the transformed schema so you can further customize it.

<section title="Example usage">

```python nocheck
from anthropic import transform_schema
from pydantic import TypeAdapter

# First convert Pydantic model to JSON schema, then transform
schema = TypeAdapter(ContactInfo).json_schema()
schema = transform_schema(schema)
# Modify schema if needed
schema["properties"]["custom_field"] = {"type": "string"}

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}],
    output_config={
        "format": {"type": "json_schema", "schema": schema},
    },
)
```

</section>

</Tab>
<Tab title="TypeScript">

**`client.messages.parse()` with `zodOutputFormat()`**

The `parse()` method accepts a Zod schema, validates the response, and returns a `parsed_output` attribute with the inferred TypeScript type matching the schema.

<section title="Example usage">

```typescript hidelines={1}
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string(),
  planInterest: z.string()
});

const client = new Anthropic();

const response = await client.messages.parse({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: "Extract contact info: John Smith, john@example.com, interested in the Pro plan"
    }
  ],
  output_config: { format: zodOutputFormat(ContactInfo) }
});

// Guaranteed type-safe
console.log(response.parsed_output!.email);
```

</section>

</Tab>
<Tab title="C#">

**Raw JSON schemas via `OutputConfig`**

The C# SDK uses raw JSON schemas built programmatically with `JsonSerializer.SerializeToElement`. Deserialize the response JSON with `JsonSerializer.Deserialize`.

<section title="Example usage">

```csharp
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

var client = new AnthropicClient();

var response = await client.Messages.Create(new MessageCreateParams
{
    Model = "claude-opus-4-6",
    MaxTokens = 1024,
    Messages = [new() {
        Role = Role.User,
        Content = "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan."
    }],
    OutputConfig = new OutputConfig
    {
        Format = new JsonOutputFormat
        {
            Schema = new Dictionary<string, JsonElement>
            {
                ["type"] = JsonSerializer.SerializeToElement("object"),
                ["properties"] = JsonSerializer.SerializeToElement(new
                {
                    name = new { type = "string" },
                    email = new { type = "string" },
                    plan_interest = new { type = "string" },
                }),
                ["required"] = JsonSerializer.SerializeToElement(
                    new[] { "name", "email", "plan_interest" }),
                ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
            },
        },
    },
});

var json = (response.Content.First().Value as TextBlock)!.Text;
// JSON is guaranteed to match the schema
var contact = JsonSerializer.Deserialize<Dictionary<string, object>>(json);
Console.WriteLine($"{contact["name"]} ({contact["email"]})");
```

</section>

</Tab>
<Tab title="Go">

**Raw JSON schemas via `OutputConfigParam`**

The Go SDK works with raw JSON schemas. Define a Go struct with json tags, generate the JSON schema (for example, using `invopop/jsonschema`), and unmarshal the response text into your struct.

<section title="Example usage">

```go hidelines={1..2,4..7,27..28,-1}
package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/invopop/jsonschema"
)

type ContactInfo struct {
	Name         string `json:"name" jsonschema:"description=Full name"`
	Email        string `json:"email" jsonschema:"description=Email address"`
	PlanInterest string `json:"plan_interest" jsonschema:"description=Plan type"`
}

func generateSchema(v any) map[string]any {
	r := jsonschema.Reflector{AllowAdditionalProperties: false, DoNotReference: true}
	s := r.Reflect(v)
	b, _ := json.Marshal(s)
	var m map[string]any
	json.Unmarshal(b, &m)
	return m
}

func main() {
	client := anthropic.NewClient()
	schema := generateSchema(&ContactInfo{})

	message, _ := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock(
				"Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan.",
			)),
		},
		OutputConfig: anthropic.OutputConfigParam{
			Format: anthropic.JSONOutputFormatParam{
				Schema: schema,
			},
		},
	})

	for _, block := range message.Content {
		switch variant := block.AsAny().(type) {
		case anthropic.TextBlock:
			var contact ContactInfo
			json.Unmarshal([]byte(variant.Text), &contact)
			fmt.Printf("%s (%s)\n", contact.Name, contact.Email)
		}
	}
}
```

</section>

</Tab>
<Tab title="Java">

**`outputConfig(Class<T>)` method**

Pass a Java class to `outputConfig()` and the SDK automatically derives a JSON schema, validates it, and returns a `StructuredMessageCreateParams<T>`. Access the parsed result via `response.content().get(0).asText().text()`.

<section title="Example usage">

```java hidelines={1..6}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.StructuredMessage;
import com.anthropic.models.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;

class ContactInfo {
    public String name;
    public String email;
    public String planInterest;
}

public class StructuredOutputExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        StructuredMessageCreateParams<ContactInfo> createParams = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(1024)
            .outputConfig(ContactInfo.class)
            .addUserMessage("Extract contact info: John Smith, john@example.com, interested in the Pro plan")
            .build();

        StructuredMessage<ContactInfo> response = client.messages().create(createParams);
        ContactInfo contact = response.content().get(0).asText().text();
        System.out.println(contact.name + " (" + contact.email + ")");
    }
}
```

</section>

<section title="Generic type erasure">

Generic type information for fields is retained in the class's metadata, but generic type erasure applies in other scopes. While a JSON schema can be derived from a `BookList.books` field with type `List<Book>`, a valid JSON schema cannot be derived from a local variable of that same type.

If an error occurs while converting a JSON response to a Java class instance, the error message includes the JSON response to assist in diagnosis. If your JSON response may contain sensitive information, avoid logging it directly, or ensure that you redact any sensitive details from the error message.

</section>

<section title="Local schema validation">

Structured outputs support a [subset of the JSON Schema language](/docs/en/build-with-claude/structured-outputs#json-schema-limitations). Schemas are generated automatically from classes to align with this subset. The `outputConfig(Class<T>)` method performs a validation check on the schema derived from the specified class.

Key points:

- **Local validation** occurs without sending requests to the remote AI model.
- **Remote validation** is also performed by the AI model upon receiving the JSON schema.
- **Version compatibility**: Local validation may fail while remote validation succeeds if the SDK version is outdated.
- **Disabling local validation**: Pass `JsonSchemaLocalValidation.NO` if you encounter compatibility issues:

```java hidelines={1..2,4..6,8..15,22..23}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.JsonSchemaLocalValidation;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;

class BookList {
    public java.util.List<String> books;
}

public class LocalValidationExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        StructuredMessageCreateParams<BookList> createParams = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(2048)
            .outputConfig(BookList.class, JsonSchemaLocalValidation.NO)
            .addUserMessage("List some famous late twentieth century novels.")
            .build();
    }
}
```

</section>

<section title="Streaming">

Structured outputs can also be used with streaming. As responses arrive in stream events, you need to accumulate the full response before deserializing the JSON.

Use `BetaMessageAccumulator` to collect the JSON strings from the stream. Once accumulated, call `BetaMessageAccumulator.message(Class<T>)` to convert the accumulated `BetaMessage` into a `StructuredMessage`, which automatically deserializes the JSON into your Java class.

</section>

<section title="JSON schema properties">

When a JSON schema is derived from your Java classes, all properties represented by `public` fields or `public` getter methods are included by default. Non-`public` fields and getter methods are excluded.

You can control visibility with annotations:

- `@JsonIgnore` excludes a `public` field or getter method
- `@JsonProperty` includes a non-`public` field or getter method

If you define `private` fields with `public` getter methods, the property name is derived from the getter (e.g., `private` field `myValue` with `public` method `getMyValue()` produces a `"myValue"` property). To use a non-conventional getter name, annotate the method with `@JsonProperty`.

Each class must define at least one property for the JSON schema. A validation error occurs if no fields or getter methods can produce schema properties, such as when:

- There are no fields or getter methods in the class
- All `public` members are annotated with `@JsonIgnore`
- All non-`public` members lack `@JsonProperty` annotations
- A field uses a `Map` type, which produces an empty `"properties"` field

</section>

<section title="Annotations (Jackson and Swagger)">

You can use Jackson Databind annotations to enrich the JSON schema derived from your Java classes:

```java hidelines={1..4,34}
import com.fasterxml.jackson.annotation.JsonClassDescription;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import java.util.List;

class Person {

  @JsonPropertyDescription("The first name and surname of the person")
  public String name;

  public int birthYear;

  @JsonPropertyDescription("The year the person died, or 'present' if the person is living.")
  public String deathYear;
}

@JsonClassDescription("The details of one published book")
class Book {

  public String title;
  public Person author;

  @JsonPropertyDescription("The year in which the book was first published.")
  public int publicationYear;

  @JsonIgnore
  public String genre;
}

class BookList {
  public List<Book> books;
}

public class Example { public static void main(String[] args) {} }
```

Annotation summary:

- `@JsonClassDescription`: Add a description to a class
- `@JsonPropertyDescription`: Add a description to a field or getter method
- `@JsonIgnore`: Exclude a `public` field or getter from the schema
- `@JsonProperty`: Include a non-`public` field or getter in the schema

If you use `@JsonProperty(required = false)`, the `false` value is ignored. Anthropic JSON schemas must mark all properties as required.

You can also use OpenAPI Swagger 2 `@Schema` and `@ArraySchema` annotations for type-specific constraints:

```java hidelines={1..3,19}
import io.swagger.v3.oas.annotations.media.ArraySchema;
import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;

class Article {

  @ArraySchema(minItems = 1)
  public List<String> authors;

  public String title;

  @Schema(format = "date")
  public String publicationDate;

  @Schema(minimum = "1")
  public int pageCount;
}

public class Example { public static void main(String[] args) {} }
```

Local validation checks that you haven't used any unsupported constraint keywords, but constraint values aren't validated locally. For example, an unsupported `"format"` value may pass local validation but cause a remote error.

If you use both Jackson and Swagger annotations to set the same schema field, the Jackson annotation takes precedence.

</section>

</Tab>
<Tab title="PHP">

**Raw JSON schemas via `OutputConfig::with()`**

The PHP SDK passes raw JSON schemas as associative arrays via `OutputConfig::with()`. Decode the response with `json_decode()`.

<section title="Example usage">

```php
<?php

use Anthropic\Client;
use Anthropic\Messages\OutputConfig;
use Anthropic\Messages\JSONOutputFormat;

$client = new Client();

$response = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => 'Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan.'],
    ],
    model: 'claude-opus-4-6',
    outputConfig: OutputConfig::with(format: JSONOutputFormat::with(schema: [
        'type' => 'object',
        'properties' => [
            'name' => ['type' => 'string'],
            'email' => ['type' => 'string'],
            'plan_interest' => ['type' => 'string'],
        ],
        'required' => ['name', 'email', 'plan_interest'],
        'additionalProperties' => false,
    ])),
);

$data = json_decode($response->content[0]->text, true);
echo $data['name'] . ' (' . $data['email'] . ')';
```

</section>

</Tab>
<Tab title="Ruby">

**`output_config: {format: Model}` with `parsed_output`**

Define a model class extending `Anthropic::BaseModel` and pass it as the format to `messages.create()`. The response includes a `parsed_output` attribute with a typed Ruby object.

<section title="Example usage">

```ruby
require "anthropic"

class ContactInfo < Anthropic::BaseModel
  required :name, String
  required :email, String
  required :plan_interest, String
end

client = Anthropic::Client.new

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: "Extract contact info: John Smith, john@example.com, interested in the Pro plan"
    }
  ],
  output_config: {format: ContactInfo}
)

contact = message.parsed_output
puts "#{contact.name} (#{contact.email})"
```

</section>

<section title="Advanced model features">

The Ruby SDK supports additional model definition features for richer schemas:

- **`doc:` keyword:** Add descriptions to fields for more informative schema output
- **`Anthropic::ArrayOf[T]`:** Typed arrays with `min_length` and `max_length` constraints
- **`Anthropic::EnumOf[:a, :b]`:** Enum fields with constrained values
- **`Anthropic::UnionOf[T1, T2]`:** Union types mapped to `anyOf`

```ruby
class FamousNumber < Anthropic::BaseModel
  required :value, Float
  optional :reason, String, doc: "why is this number mathematically significant?"
end

class Output < Anthropic::BaseModel
  required :numbers, Anthropic::ArrayOf[FamousNumber], min_length: 3, max_length: 5
end

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{role: "user", content: "give me some famous numbers"}],
  output_config: {format: Output}
)

message.parsed_output
# => #<Output numbers=[#<FamousNumber value=3.14159... reason="Pi is...">...]>
```

</section>

</Tab>
</Tabs>

#### How SDK transformation works

The Python and TypeScript SDKs automatically transform schemas with unsupported features:

1. **Remove unsupported constraints** (e.g., `minimum`, `maximum`, `minLength`, `maxLength`)
2. **Update descriptions** with constraint info (e.g., "Must be at least 100"), when the constraint is not directly supported with structured outputs
3. **Add `additionalProperties: false`** to all objects
4. **Filter string formats** to supported list only
5. **Validate responses** against your original schema (with all constraints)

This means Claude receives a simplified schema, but your code still enforces all constraints through validation.

**Example:** A Pydantic field with `minimum: 100` becomes a plain integer in the sent schema, but the description is updated to "Must be at least 100", and the SDK validates the response against the original constraint.

### Common use cases

<section title="Data extraction">

Extract structured data from unstructured text:

<CodeGroup>

```python Python nocheck hidelines={1..2}
from pydantic import BaseModel
from typing import List


class Invoice(BaseModel):
    invoice_number: str
    date: str
    total_amount: float
    line_items: List[dict]
    customer_name: str


response = client.messages.parse(
    model="claude-opus-4-6",
    max_tokens=4096,
    output_format=Invoice,
    messages=[
        {"role": "user", "content": f"Extract invoice data from: {invoice_text}"}
    ],
)
```

```typescript TypeScript hidelines={1}
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const client = new Anthropic();

const InvoiceSchema = z.object({
  invoice_number: z.string(),
  date: z.string(),
  total_amount: z.number(),
  line_items: z.array(z.record(z.string(), z.any())),
  customer_name: z.string()
});

const invoiceText = "Invoice #12345, Date: 2024-01-15, Total: $500.00";
const response = await client.messages.parse({
  model: "claude-opus-4-6",
  max_tokens: 4096,
  output_config: { format: zodOutputFormat(InvoiceSchema) },
  messages: [{ role: "user", content: `Extract invoice data from: ${invoiceText}` }]
});
```

```csharp C#
using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Anthropic;
using Anthropic.Models.Messages;

public class InvoiceExtraction
{
    public class Invoice
    {
        public string invoice_number { get; set; }
        public string date { get; set; }
        public double total_amount { get; set; }
        public List<Dictionary<string, object>> line_items { get; set; }
        public string customer_name { get; set; }
    }

    static async Task Main()
    {
        AnthropicClient client = new();

        string invoiceText = "Invoice #12345, Date: 2024-01-15, Total: $500.00";

        var parameters = new MessageCreateParams
        {
            Model = Model.ClaudeOpus4_6,
            MaxTokens = 4096,
            OutputConfig = new OutputConfig
            {
                Format = new JsonOutputFormat
                {
                    Schema = new Dictionary<string, JsonElement>
                    {
                        ["type"] = JsonSerializer.SerializeToElement("object"),
                        ["properties"] = JsonSerializer.SerializeToElement(new
                        {
                            invoice_number = new { type = "string" },
                            date = new { type = "string" },
                            total_amount = new { type = "number" },
                            line_items = new
                            {
                                type = "array",
                                items = new
                                {
                                    type = "object",
                                    additionalProperties = false,
                                },
                            },
                            customer_name = new { type = "string" },
                        }),
                        ["required"] = JsonSerializer.SerializeToElement(new[] { "invoice_number", "date", "total_amount", "line_items", "customer_name" }),
                        ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
                    },
                },
            },
            Messages = [new() { Role = Role.User, Content = $"Extract invoice data from: {invoiceText}" }]
        };

        var message = await client.Messages.Create(parameters);
        Console.WriteLine(message);
    }
}
```

```go Go hidelines={1..13,-10..-1}
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/anthropics/anthropic-sdk-go"
)

func main() {
	client := anthropic.NewClient()

	invoiceText := "Invoice #12345, Date: 2024-01-15, Total: $500.00"

	schema := map[string]any{
		"type":                 "object",
		"additionalProperties": false,
		"properties": map[string]any{
			"invoice_number": map[string]any{"type": "string"},
			"date":           map[string]any{"type": "string"},
			"total_amount":   map[string]any{"type": "number"},
			"line_items": map[string]any{
				"type": "array",
				"items": map[string]any{
					"type":                 "object",
					"additionalProperties": false,
					"properties": map[string]any{
						"description": map[string]any{"type": "string"},
						"quantity":    map[string]any{"type": "number"},
						"unit_price":  map[string]any{"type": "number"},
					},
					"required": []string{"description", "quantity", "unit_price"},
				},
			},
			"customer_name": map[string]any{"type": "string"},
		},
		"required": []string{"invoice_number", "date", "total_amount", "line_items", "customer_name"},
	}

	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 4096,
		OutputConfig: anthropic.OutputConfigParam{
			Format: anthropic.JSONOutputFormatParam{
				Schema: schema,
			},
		},
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock(fmt.Sprintf("Extract invoice data from: %s", invoiceText))),
		},
	})
	if err != nil {
		log.Fatal(err)
	}
	for _, block := range response.Content {
		switch variant := block.AsAny().(type) {
		case anthropic.TextBlock:
			fmt.Println(variant.Text)
		}
	}
}
```

```java Java hidelines={1..10,-1}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.StructuredMessage;
import com.anthropic.models.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class InvoiceExtraction {
    static class LineItem {
        @JsonProperty("description")
        public String description;

        @JsonProperty("quantity")
        public int quantity;

        @JsonProperty("unit_price")
        public double unitPrice;
    }

    static class Invoice {
        @JsonProperty("invoice_number")
        public String invoiceNumber;

        @JsonProperty("date")
        public String date;

        @JsonProperty("total_amount")
        public double totalAmount;

        @JsonProperty("line_items")
        public List<LineItem> lineItems;

        @JsonProperty("customer_name")
        public String customerName;
    }

    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        String invoiceText = "Invoice #12345, Date: 2024-01-15, Total: $500.00";

        StructuredMessageCreateParams<Invoice> params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(4096L)
            .outputConfig(Invoice.class)
            .addUserMessage("Extract invoice data from: " + invoiceText)
            .build();

        StructuredMessage<Invoice> response = client.messages().create(params);
        System.out.println(response);
    }
}
```

```php PHP hidelines={1..5}
<?php

use Anthropic\Client;

$client = new Client(apiKey: getenv("ANTHROPIC_API_KEY"));

$invoiceText = "Invoice #12345, Date: 2024-01-15, Total: $500.00";

$message = $client->messages->create(
    maxTokens: 4096,
    messages: [
        ['role' => 'user', 'content' => "Extract invoice data from: $invoiceText"]
    ],
    model: 'claude-opus-4-6',
    outputConfig: [
        'format' => [
            'type' => 'json_schema',
            'schema' => [
                'type' => 'object',
                'properties' => [
                    'invoice_number' => ['type' => 'string'],
                    'date' => ['type' => 'string'],
                    'total_amount' => ['type' => 'number'],
                    'line_items' => [
                        'type' => 'array',
                        'items' => [
                            'type' => 'object',
                            'additionalProperties' => false
                        ]
                    ],
                    'customer_name' => ['type' => 'string']
                ],
                'required' => ['invoice_number', 'date', 'total_amount', 'line_items', 'customer_name'],
                'additionalProperties' => false
            ]
        ]
    ],
);

echo $message;
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

invoice_text = "Invoice #12345, Date: 2024-01-15, Total: $500.00"

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 4096,
  output_config: {
    format: {
      type: :json_schema,
      schema: {
        type: "object",
        properties: {
          invoice_number: { type: "string" },
          date: { type: "string" },
          total_amount: { type: "number" },
          line_items: {
            type: "array",
            items: {
              type: "object",
              additionalProperties: false
            }
          },
          customer_name: { type: "string" }
        },
        required: ["invoice_number", "date", "total_amount", "line_items", "customer_name"],
        additionalProperties: false
      }
    }
  },
  messages: [
    { role: "user", content: "Extract invoice data from: #{invoice_text}" }
  ]
)
puts message.content.first.text
```

</CodeGroup>

</section>

<section title="Classification">

Classify content with structured categories:

<CodeGroup>

```python Python hidelines={1..3}
from anthropic import Anthropic

client = Anthropic()
from pydantic import BaseModel
from typing import List


class Classification(BaseModel):
    category: str
    confidence: float
    tags: List[str]
    sentiment: str


feedback_text = "Great product, but the delivery was slow."
response = client.messages.parse(
    model="claude-opus-4-6",
    max_tokens=1024,
    output_format=Classification,
    messages=[{"role": "user", "content": f"Classify this feedback: {feedback_text}"}],
)
```

```typescript TypeScript hidelines={1}
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const client = new Anthropic();

const ClassificationSchema = z.object({
  category: z.string(),
  confidence: z.number(),
  tags: z.array(z.string()),
  sentiment: z.string()
});

const feedbackText = "Great product, but the delivery was slow.";
const response = await client.messages.parse({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  output_config: { format: zodOutputFormat(ClassificationSchema) },
  messages: [{ role: "user", content: `Classify this feedback: ${feedbackText}` }]
});
```

```csharp C# hidelines={1..6,-1}
using System.Collections.Generic;
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

AnthropicClient client = new();

string feedbackText = "Great product, fast shipping!";

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 1024,
    Messages = [new() { Role = Role.User, Content = $"Classify this feedback: {feedbackText}" }],
    OutputConfig = new OutputConfig
    {
        Format = new JsonOutputFormat
        {
            Schema = new Dictionary<string, JsonElement>
            {
                ["type"] = JsonSerializer.SerializeToElement("object"),
                ["properties"] = JsonSerializer.SerializeToElement(new
                {
                    category = new { type = "string" },
                    confidence = new { type = "number" },
                    tags = new { type = "array", items = new { type = "string" } },
                    sentiment = new { type = "string" },
                }),
                ["required"] = JsonSerializer.SerializeToElement(new[] { "category", "confidence", "tags", "sentiment" }),
                ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
            },
        },
    },
};

var message = await client.Messages.Create(parameters);
Console.WriteLine(message);
```

```go Go hidelines={1..14,-1}
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/anthropics/anthropic-sdk-go"
)

func main() {
	client := anthropic.NewClient()

	feedbackText := "Great product, fast shipping!"

	schema := map[string]any{
		"type": "object",
		"properties": map[string]any{
			"category":   map[string]any{"type": "string"},
			"confidence": map[string]any{"type": "number"},
			"tags":       map[string]any{"type": "array", "items": map[string]any{"type": "string"}},
			"sentiment":  map[string]any{"type": "string"},
		},
		"required":             []string{"category", "confidence", "tags", "sentiment"},
		"additionalProperties": false,
	}

	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		OutputConfig: anthropic.OutputConfigParam{
			Format: anthropic.JSONOutputFormatParam{
				Schema: schema,
			},
		},
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock(fmt.Sprintf("Classify this feedback: %s", feedbackText))),
		},
	})
	if err != nil {
		log.Fatal(err)
	}
	for _, block := range response.Content {
		switch variant := block.AsAny().(type) {
		case anthropic.TextBlock:
			var result map[string]any
			json.Unmarshal([]byte(variant.Text), &result)
			fmt.Println(result)
		}
	}
}
```

```java Java hidelines={1..9,-1}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.StructuredMessage;
import com.anthropic.models.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class ClassificationExample {
    static class Classification {
        @JsonProperty("category")
        public String category;

        @JsonProperty("confidence")
        public double confidence;

        @JsonProperty("tags")
        public List<String> tags;

        @JsonProperty("sentiment")
        public String sentiment;
    }

    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        String feedbackText = "Great product, fast shipping!";

        StructuredMessageCreateParams<Classification> params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(1024L)
            .outputConfig(Classification.class)
            .addUserMessage("Classify this feedback: " + feedbackText)
            .build();

        StructuredMessage<Classification> response = client.messages().create(params);
        Classification result = response.content().get(0).asText().text();
        System.out.println(result.category + " (" + result.confidence + ")");
    }
}
```

```php PHP hidelines={1..6}
<?php

use Anthropic\Client;

$client = new Client(apiKey: getenv("ANTHROPIC_API_KEY"));

$feedbackText = "Great product, fast shipping!";

$message = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => "Classify this feedback: {$feedbackText}"]
    ],
    model: 'claude-opus-4-6',
    outputConfig: [
        'format' => [
            'type' => 'json_schema',
            'schema' => [
                'type' => 'object',
                'properties' => [
                    'category' => ['type' => 'string'],
                    'confidence' => ['type' => 'number'],
                    'tags' => ['type' => 'array', 'items' => ['type' => 'string']],
                    'sentiment' => ['type' => 'string']
                ],
                'required' => ['category', 'confidence', 'tags', 'sentiment'],
                'additionalProperties' => false
            ]
        ]
    ],
);
echo $message->content[0]->text;
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

class Classification < Anthropic::BaseModel
  required :category, String
  required :confidence, Float
  required :tags, Anthropic::ArrayOf[String]
  required :sentiment, String
end

feedback_text = "Great product, fast shipping!"

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  output_config: {format: Classification},
  messages: [
    {role: "user", content: "Classify this feedback: #{feedback_text}"}
  ]
)
puts message.parsed_output
```

</CodeGroup>

</section>

<section title="API response formatting">

Generate API-ready responses:

<CodeGroup>

```python Python hidelines={1..3}
from anthropic import Anthropic

client = Anthropic()
from pydantic import BaseModel
from typing import List, Optional


class APIResponse(BaseModel):
    status: str
    data: dict
    errors: Optional[List[dict]]
    metadata: dict


response = client.messages.parse(
    model="claude-opus-4-6",
    max_tokens=1024,
    output_format=APIResponse,
    messages=[{"role": "user", "content": "Process this request: ..."}],
)
```

```typescript TypeScript hidelines={1}
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const client = new Anthropic();

const APIResponseSchema = z.object({
  status: z.string(),
  data: z.record(z.string(), z.any()),
  errors: z.array(z.record(z.string(), z.any())).optional(),
  metadata: z.record(z.string(), z.any())
});

const response = await client.messages.parse({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  output_config: { format: zodOutputFormat(APIResponseSchema) },
  messages: [{ role: "user", content: "Process this request..." }]
});
```

```csharp C# hidelines={1..6,-1}
using System.Collections.Generic;
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

AnthropicClient client = new();

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 1024,
    Messages = [new() { Role = Role.User, Content = "Process this request: ..." }],
    OutputConfig = new OutputConfig
    {
        Format = new JsonOutputFormat
        {
            Schema = new Dictionary<string, JsonElement>
            {
                ["type"] = JsonSerializer.SerializeToElement("object"),
                ["properties"] = JsonSerializer.SerializeToElement(new
                {
                    status = new { type = "string" },
                    data = new { type = "object", additionalProperties = false },
                    errors = new
                    {
                        type = "array",
                        items = new { type = "object", additionalProperties = false },
                    },
                    metadata = new { type = "object", additionalProperties = false },
                }),
                ["required"] = JsonSerializer.SerializeToElement(new[] { "status", "data", "metadata" }),
                ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
            },
        },
    },
};

var message = await client.Messages.Create(parameters);
Console.WriteLine(message);
```

```go Go hidelines={1..13,-10..-1}
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/anthropics/anthropic-sdk-go"
)

func main() {
	client := anthropic.NewClient()

	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		OutputConfig: anthropic.OutputConfigParam{
			Format: anthropic.JSONOutputFormatParam{
				Schema: map[string]any{
					"type":                 "object",
					"additionalProperties": false,
					"properties": map[string]any{
						"status": map[string]any{
							"type": "string",
						},
						"data": map[string]any{
							"type":                 "object",
							"additionalProperties": false,
						},
						"errors": map[string]any{
							"type": "array",
							"items": map[string]any{
								"type":                 "object",
								"additionalProperties": false,
							},
						},
						"metadata": map[string]any{
							"type":                 "object",
							"additionalProperties": false,
						},
					},
					"required": []string{"status", "data", "metadata"},
				},
			},
		},
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock("Process this request: ...")),
		},
	})
	if err != nil {
		log.Fatal(err)
	}
	for _, block := range response.Content {
		switch variant := block.AsAny().(type) {
		case anthropic.TextBlock:
			fmt.Println(variant.Text)
		}
	}
}
```

```java Java hidelines={1..10,-1}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.StructuredMessage;
import com.anthropic.models.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class StructuredOutputExample {
    static class APIResponse {
        @JsonProperty("status")
        public String status;

        @JsonProperty("data")
        public Map<String, Object> data;

        @JsonProperty("errors")
        public List<Map<String, Object>> errors;

        @JsonProperty("metadata")
        public Map<String, Object> metadata;
    }

    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        StructuredMessageCreateParams<APIResponse> params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(1024L)
            .outputConfig(APIResponse.class)
            .addUserMessage("Process this request: ...")
            .build();

        StructuredMessage<APIResponse> response = client.messages().create(params);
        APIResponse result = response.content().get(0).asText().text();
        System.out.println(result.status);
    }
}
```

```php PHP hidelines={1..5}
<?php

use Anthropic\Client;

$client = new Client(apiKey: getenv("ANTHROPIC_API_KEY"));

$message = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => 'Process this request: ...']
    ],
    model: 'claude-opus-4-6',
    outputConfig: [
        'format' => [
            'type' => 'json_schema',
            'schema' => [
                'type' => 'object',
                'properties' => [
                    'status' => ['type' => 'string'],
                    'data' => ['type' => 'object', 'additionalProperties' => false],
                    'errors' => [
                        'type' => 'array',
                        'items' => ['type' => 'object', 'additionalProperties' => false]
                    ],
                    'metadata' => ['type' => 'object', 'additionalProperties' => false]
                ],
                'required' => ['status', 'data', 'metadata'],
                'additionalProperties' => false
            ]
        ]
    ],
);

echo $message;
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  output_config: {
    format: {
      type: :json_schema,
      schema: {
        type: "object",
        properties: {
          status: { type: "string" },
          data: { type: "object", additionalProperties: false },
          errors: {
            type: "array",
            items: { type: "object", additionalProperties: false }
          },
          metadata: { type: "object", additionalProperties: false }
        },
        required: ["status", "data", "metadata"],
        additionalProperties: false
      }
    }
  },
  messages: [
    { role: "user", content: "Process this request: ..." }
  ]
)
puts message.content.first.text
```

</CodeGroup>

</section>

## Strict tool use

Strict tool use validates tool parameters, ensuring Claude calls your functions with correctly-typed arguments. Use strict tool use when you need to:

- Validate tool parameters
- Build agentic workflows
- Ensure type-safe function calls
- Handle complex tools with nested properties

### Why strict tool use matters for agents

Building reliable agentic systems requires guaranteed schema conformance. Without strict mode, Claude might return incompatible types (`"2"` instead of `2`) or missing required fields, breaking your functions and causing runtime errors.

Strict tool use guarantees type-safe parameters:
- Functions receive correctly-typed arguments every time
- No need to validate and retry tool calls
- Production-ready agents that work consistently at scale

For example, suppose a booking system needs `passengers: int`. Without strict mode, Claude might provide `passengers: "two"` or `passengers: "2"`. With `strict: true`, the response will always contain `passengers: 2`.

### Quick start

<CodeGroup>

```bash Shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "What is the weather in San Francisco?"}
    ],
    "tools": [{
      "name": "get_weather",
      "description": "Get the current weather in a given location",
      "strict": true,
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          },
          "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"]
          }
        },
        "required": ["location"],
        "additionalProperties": false
      }
    }]
  }'
```

```python Python hidelines={1..4,-1}
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "strict": True,  # Enable strict mode
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit of temperature, either 'celsius' or 'fahrenheit'",
                    },
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        }
    ],
)
print(response.content)
```

```typescript TypeScript hidelines={1..2}
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: "What's the weather like in San Francisco?"
    }
  ],
  tools: [
    {
      name: "get_weather",
      description: "Get the current weather in a given location",
      strict: true, // Enable strict mode
      input_schema: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "The city and state, e.g. San Francisco, CA"
          },
          unit: {
            type: "string",
            enum: ["celsius", "fahrenheit"]
          }
        },
        required: ["location"],
        additionalProperties: false
      }
    }
  ]
});
console.log(response.content);
```

```csharp C#
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

public class Program
{
    public static async Task Main(string[] args)
    {
        AnthropicClient client = new();

        var parameters = new MessageCreateParams
        {
            Model = Model.ClaudeOpus4_6,
            MaxTokens = 1024,
            Messages = [new() { Role = Role.User, Content = "What's the weather like in San Francisco?" }],
            Tools = [
                new ToolUnion(new Tool()
                {
                    Name = "get_weather",
                    Description = "Get the current weather in a given location",
                    Strict = true,
                    InputSchema = new InputSchema(new Dictionary<string, JsonElement>
                    {
                        ["properties"] = JsonSerializer.SerializeToElement(new Dictionary<string, object>
                        {
                            ["location"] = new { type = "string", description = "The city and state, e.g. San Francisco, CA" },
                            ["unit"] = new { type = "string", @enum = new[] { "celsius", "fahrenheit" } },
                        }),
                        ["required"] = JsonSerializer.SerializeToElement(new[] { "location" }),
                        ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
                    }),
                }),
            ]
        };

        var message = await client.Messages.Create(parameters);
        Console.WriteLine(message);
    }
}
```

```go Go hidelines={1..13,-5..-1}
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/anthropics/anthropic-sdk-go"
)

func main() {
	client := anthropic.NewClient()

	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock("What's the weather like in San Francisco?")),
		},
		Tools: []anthropic.ToolUnionParam{
			{OfTool: &anthropic.ToolParam{
				Name:        "get_weather",
				Description: anthropic.String("Get the current weather in a given location"),
				Strict:      anthropic.Bool(true),
				InputSchema: anthropic.ToolInputSchemaParam{
					Properties: map[string]any{
						"location": map[string]any{
							"type":        "string",
							"description": "The city and state, e.g. San Francisco, CA",
						},
						"unit": map[string]any{
							"type": "string",
							"enum": []string{"celsius", "fahrenheit"},
						},
					},
					Required: []string{"location"},
					ExtraFields: map[string]any{
						"additionalProperties": false,
					},
				}}},
		},
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(response.Content)
}
```

```java Java hidelines={1..13,-1}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.JsonValue;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;
import com.anthropic.models.messages.Tool;
import com.anthropic.models.messages.Tool.InputSchema;
import java.util.List;
import java.util.Map;

public class StrictToolExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        InputSchema schema = InputSchema.builder()
            .properties(
                JsonValue.from(
                    Map.of(
                        "location", Map.of(
                            "type", "string",
                            "description", "The city and state, e.g. San Francisco, CA"
                        ),
                        "unit", Map.of(
                            "type", "string",
                            "enum", List.of("celsius", "fahrenheit")
                        )
                    )
                )
            )
            .putAdditionalProperty("required", JsonValue.from(List.of("location")))
            .putAdditionalProperty("additionalProperties", JsonValue.from(false))
            .build();

        MessageCreateParams params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(1024L)
            .addUserMessage("What's the weather like in San Francisco?")
            .addTool(
                Tool.builder()
                    .name("get_weather")
                    .description("Get the current weather in a given location")
                    .strict(true)
                    .inputSchema(schema)
                    .build()
            )
            .build();

        Message response = client.messages().create(params);
        System.out.println(response.content());
    }
}
```

```php PHP hidelines={1..6}
<?php

use Anthropic\Client;

$client = new Client(apiKey: getenv("ANTHROPIC_API_KEY"));

$message = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => "What's the weather like in San Francisco?"]
    ],
    model: 'claude-opus-4-6',
    tools: [
        [
            'name' => 'get_weather',
            'description' => 'Get the current weather in a given location',
            'strict' => true,
            'input_schema' => [
                'type' => 'object',
                'properties' => [
                    'location' => [
                        'type' => 'string',
                        'description' => 'The city and state, e.g. San Francisco, CA'
                    ],
                    'unit' => [
                        'type' => 'string',
                        'enum' => ['celsius', 'fahrenheit']
                    ]
                ],
                'required' => ['location'],
                'additionalProperties' => false
            ]
        ]
    ],
);

echo $message;
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    { role: "user", content: "What's the weather like in San Francisco?" }
  ],
  tools: [
    {
      name: "get_weather",
      description: "Get the current weather in a given location",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "The city and state, e.g. San Francisco, CA"
          },
          unit: {
            type: "string",
            enum: ["celsius", "fahrenheit"]
          }
        },
        required: ["location"],
        additionalProperties: false
      }
    }
  ]
)
puts message.content
```

</CodeGroup>

**Response format:** Tool use blocks with validated inputs in `response.content[x].input`

```json
{
  "type": "tool_use",
  "name": "get_weather",
  "input": {
    "location": "San Francisco, CA"
  }
}
```

**Guarantees:**
- Tool `input` strictly follows the `input_schema`
- Tool `name` is always valid (from provided tools or server tools)

### How it works

<Steps>
  <Step title="Define your tool schema">
    Create a JSON schema for your tool's `input_schema`. The schema uses standard JSON Schema format with some limitations (see [JSON Schema limitations](#json-schema-limitations)).
  </Step>
  <Step title="Add strict: true">
    Set `"strict": true` as a top-level property in your tool definition, alongside `name`, `description`, and `input_schema`.
  </Step>
  <Step title="Handle tool calls">
    When Claude uses the tool, the `input` field in the tool_use block will strictly follow your `input_schema`, and the `name` will always be valid.
  </Step>
</Steps>

### Common use cases

<section title="Validated tool inputs">

Ensure tool parameters exactly match your schema:

<CodeGroup>

```python Python hidelines={1..3}
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Search for flights to Tokyo departing June 1, 2026"}],
    tools=[
        {
            "name": "search_flights",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "departure_date": {"type": "string", "format": "date"},
                    "passengers": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    },
                },
                "required": ["destination", "departure_date"],
                "additionalProperties": False,
            },
        }
    ],
)
```

```typescript TypeScript hidelines={1..4}
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const searchFlightsTool: Anthropic.Tool = {
  name: "search_flights",
  strict: true,
  input_schema: {
    type: "object",
    properties: {
      destination: { type: "string" },
      departure_date: { type: "string", format: "date" },
      passengers: { type: "integer", enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }
    },
    required: ["destination", "departure_date"],
    additionalProperties: false
  }
};

const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Search for flights to Tokyo departing June 1, 2026" }],
  tools: [searchFlightsTool]
});
```

```csharp C#
using System;
using System.Text.Json;
using System.Threading.Tasks;
using Anthropic;
using Anthropic.Models.Messages;

class Program
{
    static async Task Main(string[] args)
    {
        AnthropicClient client = new()
        {
            ApiKey = Environment.GetEnvironmentVariable("ANTHROPIC_API_KEY")
        };

        var parameters = new MessageCreateParams
        {
            Model = Model.ClaudeOpus4_6,
            MaxTokens = 1024,
            Messages = [new() { Role = Role.User, Content = "Search for flights to Tokyo departing June 1, 2026" }],
            Tools = [
                new ToolUnion(new Tool()
                {
                    Name = "search_flights",
                    Strict = true,
                    InputSchema = new InputSchema(new Dictionary<string, JsonElement>
                    {
                        ["properties"] = JsonSerializer.SerializeToElement(new Dictionary<string, object>
                        {
                            ["destination"] = new { type = "string" },
                            ["departure_date"] = new { type = "string", format = "date" },
                            ["passengers"] = new { type = "integer", @enum = new[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 } },
                        }),
                        ["required"] = JsonSerializer.SerializeToElement(new[] { "destination", "departure_date" }),
                        ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
                    }),
                }),
            ]
        };

        var message = await client.Messages.Create(parameters);
        Console.WriteLine(message);
    }
}
```

```go Go hidelines={1..13,-5..-1}
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/anthropics/anthropic-sdk-go"
)

func main() {
	client := anthropic.NewClient()

	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock("Search for flights to Tokyo departing June 1, 2026")),
		},
		Tools: []anthropic.ToolUnionParam{
			{OfTool: &anthropic.ToolParam{
				Name:   "search_flights",
				Strict: anthropic.Bool(true),
				InputSchema: anthropic.ToolInputSchemaParam{
					Properties: map[string]any{
						"destination": map[string]any{
							"type": "string",
						},
						"departure_date": map[string]any{
							"type":   "string",
							"format": "date",
						},
						"passengers": map[string]any{
							"type": "integer",
							"enum": []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
						},
					},
					Required: []string{"destination", "departure_date"},
					ExtraFields: map[string]any{
						"additionalProperties": false,
					},
				}}},
		},
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(response)
}
```

```java Java hidelines={1..13,-1}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.JsonValue;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;
import com.anthropic.models.messages.Tool;
import com.anthropic.models.messages.Tool.InputSchema;
import java.util.List;
import java.util.Map;

public class StrictToolExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        InputSchema schema = InputSchema.builder()
            .properties(
                JsonValue.from(
                    Map.of(
                        "destination", Map.of("type", "string"),
                        "departure_date", Map.of("type", "string", "format", "date"),
                        "passengers", Map.of(
                            "type", "integer",
                            "enum", List.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                        )
                    )
                )
            )
            .putAdditionalProperty("required", JsonValue.from(List.of("destination", "departure_date")))
            .putAdditionalProperty("additionalProperties", JsonValue.from(false))
            .build();

        MessageCreateParams params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(1024L)
            .addUserMessage("Search for flights to Tokyo departing June 1, 2026")
            .addTool(
                Tool.builder()
                    .name("search_flights")
                    .strict(true)
                    .inputSchema(schema)
                    .build()
            )
            .build();

        Message response = client.messages().create(params);
        System.out.println(response);
    }
}
```

```php PHP hidelines={1..6}
<?php

use Anthropic\Client;

$client = new Client(apiKey: getenv("ANTHROPIC_API_KEY"));

$message = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => 'Search for flights to Tokyo departing June 1, 2026']
    ],
    model: 'claude-opus-4-6',
    tools: [
        [
            'name' => 'search_flights',
            'strict' => true,
            'input_schema' => [
                'type' => 'object',
                'properties' => [
                    'destination' => ['type' => 'string'],
                    'departure_date' => ['type' => 'string', 'format' => 'date'],
                    'passengers' => [
                        'type' => 'integer',
                        'enum' => [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    ]
                ],
                'required' => ['destination', 'departure_date'],
                'additionalProperties' => false
            ]
        ]
    ],
);
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    { role: "user", content: "Search for flights to Tokyo departing June 1, 2026" }
  ],
  tools: [
    {
      name: "search_flights",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          destination: { type: "string" },
          departure_date: { type: "string", format: "date" },
          passengers: {
            type: "integer",
            enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
          }
        },
        required: ["destination", "departure_date"],
        additionalProperties: false
      }
    }
  ]
)
puts message
```

</CodeGroup>

</section>

<section title="Agentic workflow with multiple validated tools">

Build reliable multi-step agents with guaranteed tool parameters:

<CodeGroup>

```python Python hidelines={1..3}
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026",
        }
    ],
    tools=[
        {
            "name": "search_flights",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "departure_date": {"type": "string", "format": "date"},
                    "travelers": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6]},
                },
                "required": ["origin", "destination", "departure_date"],
                "additionalProperties": False,
            },
        },
        {
            "name": "search_hotels",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "check_in": {"type": "string", "format": "date"},
                    "guests": {"type": "integer", "enum": [1, 2, 3, 4]},
                },
                "required": ["city", "check_in"],
                "additionalProperties": False,
            },
        },
    ],
)
```

```typescript TypeScript hidelines={1..4}
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const tools: Anthropic.Tool[] = [
  {
    name: "search_flights",
    strict: true,
    input_schema: {
      type: "object",
      properties: {
        origin: { type: "string" },
        destination: { type: "string" },
        departure_date: { type: "string", format: "date" },
        travelers: { type: "integer", enum: [1, 2, 3, 4, 5, 6] }
      },
      required: ["origin", "destination", "departure_date"],
      additionalProperties: false
    }
  },
  {
    name: "search_hotels",
    strict: true,
    input_schema: {
      type: "object",
      properties: {
        city: { type: "string" },
        check_in: { type: "string", format: "date" },
        guests: { type: "integer", enum: [1, 2, 3, 4] }
      },
      required: ["city", "check_in"],
      additionalProperties: false
    }
  }
];

const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content:
        "Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026",
    },
  ],
  tools: tools
});
```

```csharp C#
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

class Program
{
    static async Task Main(string[] args)
    {
        AnthropicClient client = new();

        var parameters = new MessageCreateParams
        {
            Model = Model.ClaudeOpus4_6,
            MaxTokens = 1024,
            Messages = [new() { Role = Role.User, Content = "Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026" }],
            Tools = [
                new ToolUnion(new Tool()
                {
                    Name = "search_flights",
                    Strict = true,
                    InputSchema = new InputSchema(new Dictionary<string, JsonElement>
                    {
                        ["properties"] = JsonSerializer.SerializeToElement(new Dictionary<string, object>
                        {
                            ["origin"] = new { type = "string" },
                            ["destination"] = new { type = "string" },
                            ["departure_date"] = new { type = "string", format = "date" },
                            ["travelers"] = new { type = "integer", @enum = new[] { 1, 2, 3, 4, 5, 6 } },
                        }),
                        ["required"] = JsonSerializer.SerializeToElement(new[] { "origin", "destination", "departure_date" }),
                        ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
                    }),
                }),
                new ToolUnion(new Tool()
                {
                    Name = "search_hotels",
                    Strict = true,
                    InputSchema = new InputSchema(new Dictionary<string, JsonElement>
                    {
                        ["properties"] = JsonSerializer.SerializeToElement(new Dictionary<string, object>
                        {
                            ["city"] = new { type = "string" },
                            ["check_in"] = new { type = "string", format = "date" },
                            ["guests"] = new { type = "integer", @enum = new[] { 1, 2, 3, 4 } },
                        }),
                        ["required"] = JsonSerializer.SerializeToElement(new[] { "city", "check_in" }),
                        ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
                    }),
                }),
            ]
        };

        var message = await client.Messages.Create(parameters);
        Console.WriteLine(message);
    }
}
```

```go Go hidelines={1..13,-5..-1}
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/anthropics/anthropic-sdk-go"
)

func main() {
	client := anthropic.NewClient()

	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock("Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026")),
		},
		Tools: []anthropic.ToolUnionParam{
			{OfTool: &anthropic.ToolParam{
				Name:   "search_flights",
				Strict: anthropic.Bool(true),
				InputSchema: anthropic.ToolInputSchemaParam{
					Properties: map[string]any{
						"origin":         map[string]any{"type": "string"},
						"destination":    map[string]any{"type": "string"},
						"departure_date": map[string]any{"type": "string", "format": "date"},
						"travelers":      map[string]any{"type": "integer", "enum": []int{1, 2, 3, 4, 5, 6}},
					},
					Required: []string{"origin", "destination", "departure_date"},
					ExtraFields: map[string]any{
						"additionalProperties": false,
					},
				}}},
			{OfTool: &anthropic.ToolParam{
				Name:   "search_hotels",
				Strict: anthropic.Bool(true),
				InputSchema: anthropic.ToolInputSchemaParam{
					Properties: map[string]any{
						"city":     map[string]any{"type": "string"},
						"check_in": map[string]any{"type": "string", "format": "date"},
						"guests":   map[string]any{"type": "integer", "enum": []int{1, 2, 3, 4}},
					},
					Required: []string{"city", "check_in"},
					ExtraFields: map[string]any{
						"additionalProperties": false,
					},
				}}},
		},
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(response)
}
```

```java Java hidelines={1..13,-1}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.JsonValue;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;
import com.anthropic.models.messages.Tool;
import com.anthropic.models.messages.Tool.InputSchema;
import java.util.List;
import java.util.Map;

public class StrictToolExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        InputSchema flightsSchema = InputSchema.builder()
            .properties(
                JsonValue.from(
                    Map.of(
                        "origin", Map.of("type", "string"),
                        "destination", Map.of("type", "string"),
                        "departure_date", Map.of("type", "string", "format", "date"),
                        "travelers", Map.of("type", "integer", "enum", List.of(1, 2, 3, 4, 5, 6))
                    )
                )
            )
            .putAdditionalProperty("required", JsonValue.from(List.of("origin", "destination", "departure_date")))
            .putAdditionalProperty("additionalProperties", JsonValue.from(false))
            .build();

        InputSchema hotelsSchema = InputSchema.builder()
            .properties(
                JsonValue.from(
                    Map.of(
                        "city", Map.of("type", "string"),
                        "check_in", Map.of("type", "string", "format", "date"),
                        "guests", Map.of("type", "integer", "enum", List.of(1, 2, 3, 4))
                    )
                )
            )
            .putAdditionalProperty("required", JsonValue.from(List.of("city", "check_in")))
            .putAdditionalProperty("additionalProperties", JsonValue.from(false))
            .build();

        MessageCreateParams params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(1024L)
            .addUserMessage("Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026")
            .addTool(
                Tool.builder()
                    .name("search_flights")
                    .strict(true)
                    .inputSchema(flightsSchema)
                    .build()
            )
            .addTool(
                Tool.builder()
                    .name("search_hotels")
                    .strict(true)
                    .inputSchema(hotelsSchema)
                    .build()
            )
            .build();

        Message response = client.messages().create(params);
        System.out.println(response);
    }
}
```

```php PHP hidelines={1..6}
<?php

use Anthropic\Client;

$client = new Client(apiKey: getenv("ANTHROPIC_API_KEY"));

$message = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => 'Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026']
    ],
    model: 'claude-opus-4-6',
    tools: [
        [
            'name' => 'search_flights',
            'strict' => true,
            'input_schema' => [
                'type' => 'object',
                'properties' => [
                    'origin' => ['type' => 'string'],
                    'destination' => ['type' => 'string'],
                    'departure_date' => ['type' => 'string', 'format' => 'date'],
                    'travelers' => ['type' => 'integer', 'enum' => [1, 2, 3, 4, 5, 6]]
                ],
                'required' => ['origin', 'destination', 'departure_date'],
                'additionalProperties' => false
            ]
        ],
        [
            'name' => 'search_hotels',
            'strict' => true,
            'input_schema' => [
                'type' => 'object',
                'properties' => [
                    'city' => ['type' => 'string'],
                    'check_in' => ['type' => 'string', 'format' => 'date'],
                    'guests' => ['type' => 'integer', 'enum' => [1, 2, 3, 4]]
                ],
                'required' => ['city', 'check_in'],
                'additionalProperties' => false
            ]
        ]
    ],
);

echo $message->content[0]->text;
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    { role: "user", content: "Help me plan a trip from New York to Paris for 2 people, departing June 1, 2026" }
  ],
  tools: [
    {
      name: "search_flights",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          origin: { type: "string" },
          destination: { type: "string" },
          departure_date: { type: "string", format: "date" },
          travelers: { type: "integer", enum: [1, 2, 3, 4, 5, 6] }
        },
        required: ["origin", "destination", "departure_date"],
        additionalProperties: false
      }
    },
    {
      name: "search_hotels",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          city: { type: "string" },
          check_in: { type: "string", format: "date" },
          guests: { type: "integer", enum: [1, 2, 3, 4] }
        },
        required: ["city", "check_in"],
        additionalProperties: false
      }
    }
  ]
)
puts message
```

</CodeGroup>

</section>

## Using both features together

JSON outputs and strict tool use solve different problems and can be used together:

- **JSON outputs** control Claude's response format (what Claude says)
- **Strict tool use** validates tool parameters (how Claude calls your functions)

When combined, Claude can call tools with guaranteed-valid parameters AND return structured JSON responses. This is useful for agentic workflows where you need both reliable tool calls and structured final outputs.

<CodeGroup>

```python Python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Help me plan a trip to Paris departing May 15, 2026"}
    ],
    # JSON outputs: structured response format
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["summary", "next_steps"],
                "additionalProperties": False,
            },
        }
    },
    # Strict tool use: guaranteed tool parameters
    tools=[
        {
            "name": "search_flights",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                },
                "required": ["destination", "date"],
                "additionalProperties": False,
            },
        }
    ],
)
```

```typescript TypeScript
const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Help me plan a trip to Paris departing May 15, 2026" }],
  // JSON outputs: structured response format
  output_config: {
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          summary: { type: "string" },
          next_steps: { type: "array", items: { type: "string" } }
        },
        required: ["summary", "next_steps"],
        additionalProperties: false
      }
    }
  },
  // Strict tool use: guaranteed tool parameters
  tools: [
    {
      name: "search_flights",
      description: "Search for available flights to a destination on a specific date",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          destination: { type: "string" },
          date: { type: "string", format: "date" }
        },
        required: ["destination", "date"],
        additionalProperties: false
      }
    }
  ]
});

// Claude may call the tool first (tool_use) or respond with JSON (text)
console.log("Stop reason:", response.stop_reason);
for (const block of response.content) {
  if (block.type === "tool_use") {
    console.log(`Tool call: ${block.name}(${JSON.stringify(block.input)})`);
  } else if (block.type === "text") {
    console.log("Response:", block.text);
  }
}
```

```csharp C# hidelines={1..6,-1}
using System.Collections.Generic;
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

AnthropicClient client = new();

var parameters = new MessageCreateParams
{
    Model = Model.ClaudeOpus4_6,
    MaxTokens = 1024,
    Messages = [new() { Role = Role.User, Content = "Help me plan a trip to Paris departing May 15, 2026" }],
    // JSON outputs: structured response format
    OutputConfig = new OutputConfig
    {
        Format = new JsonOutputFormat
        {
            Schema = new Dictionary<string, JsonElement>
            {
                ["type"] = JsonSerializer.SerializeToElement("object"),
                ["properties"] = JsonSerializer.SerializeToElement(new
                {
                    summary = new { type = "string" },
                    next_steps = new { type = "array", items = new { type = "string" } },
                }),
                ["required"] = JsonSerializer.SerializeToElement(new[] { "summary", "next_steps" }),
                ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
            },
        },
    },
    // Strict tool use: guaranteed tool parameters
    Tools =
    [
        new Tool
        {
            Name = "search_flights",
            Strict = true,
            InputSchema = new InputSchema(new Dictionary<string, JsonElement>
            {
                ["properties"] = JsonSerializer.SerializeToElement(new Dictionary<string, object>
                {
                    ["destination"] = new { type = "string" },
                    ["date"] = new { type = "string", format = "date" },
                }),
                ["required"] = JsonSerializer.SerializeToElement(new[] { "destination", "date" }),
                ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
            }),
        }
    ],
};

var message = await client.Messages.Create(parameters);
Console.WriteLine(message);
```

```go Go hidelines={1..13,-5..-1}
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/anthropics/anthropic-sdk-go"
)

func main() {
	client := anthropic.NewClient()

	response, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock("Help me plan a trip to Paris departing May 15, 2026")),
		},
		// JSON outputs: structured response format
		OutputConfig: anthropic.OutputConfigParam{
			Format: anthropic.JSONOutputFormatParam{
				Schema: map[string]any{
					"type":                 "object",
					"additionalProperties": false,
					"properties": map[string]any{
						"summary":    map[string]any{"type": "string"},
						"next_steps": map[string]any{"type": "array", "items": map[string]any{"type": "string"}},
					},
					"required": []string{"summary", "next_steps"},
				},
			},
		},
		// Strict tool use: guaranteed tool parameters
		Tools: []anthropic.ToolUnionParam{
			{OfTool: &anthropic.ToolParam{
				Name:   "search_flights",
				Strict: anthropic.Bool(true),
				InputSchema: anthropic.ToolInputSchemaParam{
					Properties: map[string]any{
						"destination": map[string]any{"type": "string"},
						"date":        map[string]any{"type": "string", "format": "date"},
					},
					Required: []string{"destination", "date"},
					ExtraFields: map[string]any{
						"additionalProperties": false,
					},
				}}},
		},
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(response.Content)
}
```

```java Java hidelines={1..15,-1}
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.core.JsonValue;
import com.anthropic.models.messages.JsonOutputFormat;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;
import com.anthropic.models.messages.OutputConfig;
import com.anthropic.models.messages.Tool;
import com.anthropic.models.messages.Tool.InputSchema;
import java.util.List;
import java.util.Map;

public class StructuredOutputExample {
    public static void main(String[] args) {
        AnthropicClient client = AnthropicOkHttpClient.fromEnv();

        // JSON outputs: structured response format
        JsonOutputFormat.Schema outputSchema = JsonOutputFormat.Schema.builder()
            .putAdditionalProperty("type", JsonValue.from("object"))
            .putAdditionalProperty("properties", JsonValue.from(Map.of(
                "summary", Map.of("type", "string"),
                "next_steps", Map.of("type", "array", "items", Map.of("type", "string"))
            )))
            .putAdditionalProperty("required", JsonValue.from(List.of("summary", "next_steps")))
            .putAdditionalProperty("additionalProperties", JsonValue.from(false))
            .build();

        // Strict tool use: guaranteed tool parameters
        InputSchema toolSchema = InputSchema.builder()
            .properties(JsonValue.from(Map.of(
                "destination", Map.of("type", "string"),
                "date", Map.of("type", "string", "format", "date")
            )))
            .putAdditionalProperty("required", JsonValue.from(List.of("destination", "date")))
            .putAdditionalProperty("additionalProperties", JsonValue.from(false))
            .build();

        MessageCreateParams params = MessageCreateParams.builder()
            .model(Model.CLAUDE_OPUS_4_6)
            .maxTokens(1024L)
            .addUserMessage("Help me plan a trip to Paris departing May 15, 2026")
            .outputConfig(OutputConfig.builder()
                .format(JsonOutputFormat.builder().schema(outputSchema).build())
                .build())
            .addTool(Tool.builder()
                .name("search_flights")
                .description("Search for available flights to a destination on a specific date")
                .strict(true)
                .inputSchema(toolSchema)
                .build())
            .build();

        Message response = client.messages().create(params);
        System.out.println(response);
    }
}
```

```php PHP hidelines={1..6}
<?php

use Anthropic\Client;

$client = new Client(apiKey: getenv("ANTHROPIC_API_KEY"));

$message = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => 'Help me plan a trip to Paris departing May 15, 2026']
    ],
    model: 'claude-opus-4-6',
    // JSON outputs: structured response format
    outputConfig: [
        'format' => [
            'type' => 'json_schema',
            'schema' => [
                'type' => 'object',
                'properties' => [
                    'summary' => ['type' => 'string'],
                    'next_steps' => ['type' => 'array', 'items' => ['type' => 'string']]
                ],
                'required' => ['summary', 'next_steps'],
                'additionalProperties' => false
            ]
        ]
    ],
    // Strict tool use: guaranteed tool parameters
    tools: [
        [
            'name' => 'search_flights',
            'strict' => true,
            'input_schema' => [
                'type' => 'object',
                'properties' => [
                    'destination' => ['type' => 'string'],
                    'date' => ['type' => 'string', 'format' => 'date']
                ],
                'required' => ['destination', 'date'],
                'additionalProperties' => false
            ]
        ]
    ],
);
echo $message;
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {role: "user", content: "Help me plan a trip to Paris departing May 15, 2026"}
  ],
  # JSON outputs: structured response format
  output_config: {
    format: {
      type: :json_schema,
      schema: {
        type: "object",
        properties: {
          summary: {type: "string"},
          next_steps: {type: "array", items: {type: "string"}}
        },
        required: ["summary", "next_steps"],
        additionalProperties: false
      }
    }
  },
  # Strict tool use: guaranteed tool parameters
  tools: [
    {
      name: "search_flights",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          destination: {type: "string"},
          date: {type: "string", format: "date"}
        },
        required: ["destination", "date"],
        additionalProperties: false
      }
    }
  ]
)
puts message
```

</CodeGroup>

## Important considerations

### Grammar compilation and caching

Structured outputs use constrained sampling with compiled grammar artifacts. This introduces some performance characteristics to be aware of:

- **First request latency:** The first time you use a specific schema, there is additional latency while the grammar compiles
- **Automatic caching:** Compiled grammars are cached for 24 hours from last use, making subsequent requests much faster
- **Cache invalidation:** The cache is invalidated if you change:
  - The JSON schema structure
  - The set of tools in your request (when using both structured outputs and tool use)
  - Changing only `name` or `description` fields does not invalidate the cache

### Prompt modification and token costs

When using structured outputs, Claude automatically receives an additional system prompt explaining the expected output format. This means:

- Your input token count is slightly higher
- The injected prompt costs you tokens like any other system prompt
- Changing the `output_config.format` parameter will invalidate any [prompt cache](/docs/en/build-with-claude/prompt-caching) for that conversation thread

### JSON Schema limitations

Structured outputs support standard JSON Schema with some limitations. Both JSON outputs and strict tool use share these limitations.

<section title="Supported features">

- All basic types: object, array, string, integer, number, boolean, null
- `enum` (strings, numbers, bools, or nulls only - no complex types)
- `const`
- `anyOf` and `allOf` (with limitations - `allOf` with `$ref` not supported)
- `$ref`, `$def`, and `definitions` (external `$ref` not supported)
- `default` property for all supported types
- `required` and `additionalProperties` (must be set to `false` for objects)
- String formats: `date-time`, `time`, `date`, `duration`, `email`, `hostname`, `uri`, `ipv4`, `ipv6`, `uuid`
- Array `minItems` (only values 0 and 1 supported)

</section>

<section title="Not supported">

- Recursive schemas
- Complex types within enums
- External `$ref` (e.g., `'$ref': 'http://...'`)
- Numerical constraints (`minimum`, `maximum`, `multipleOf`, etc.)
- String constraints (`minLength`, `maxLength`)
- Array constraints beyond `minItems` of 0 or 1
- `additionalProperties` set to anything other than `false`

If you use an unsupported feature, you'll receive a 400 error with details.

</section>

<section title="Pattern support (regex)">

**Supported regex features:**
- Full matching (`^...$`) and partial matching
- Quantifiers: `*`, `+`, `?`, simple `{n,m}` cases
- Character classes: `[]`, `.`, `\d`, `\w`, `\s`
- Groups: `(...)`

**NOT supported:**
- Backreferences to groups (e.g., `\1`, `\2`)
- Lookahead/lookbehind assertions (e.g., `(?=...)`, `(?!...)`)
- Word boundaries: `\b`, `\B`
- Complex `{n,m}` quantifiers with large ranges

Simple regex patterns work well. Complex patterns may result in 400 errors.

</section>

<Tip>
The Python and TypeScript SDKs can automatically transform schemas with unsupported features by removing them and adding constraints to field descriptions. See [SDK-specific methods](#sdk-specific-methods) for details.
</Tip>

### Property ordering

When using structured outputs, properties in objects maintain their defined ordering from your schema, with one important caveat: **required properties appear first, followed by optional properties**.

For example, given this schema:

```json
{
  "type": "object",
  "properties": {
    "notes": { "type": "string" },
    "name": { "type": "string" },
    "email": { "type": "string" },
    "age": { "type": "integer" }
  },
  "required": ["name", "email"],
  "additionalProperties": false
}
```

The output will order properties as:

1. `name` (required, in schema order)
2. `email` (required, in schema order)
3. `notes` (optional, in schema order)
4. `age` (optional, in schema order)

This means the output might look like:

```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "notes": "Interested in enterprise plan",
  "age": 35
}
```

If property order in the output is important to your application, ensure all properties are marked as required, or account for this reordering in your parsing logic.

### Invalid outputs

While structured outputs guarantee schema compliance in most cases, there are scenarios where the output may not match your schema:

**Refusals** (`stop_reason: "refusal"`)

Claude maintains its safety and helpfulness properties even when using structured outputs. If Claude refuses a request for safety reasons:

- The response has `stop_reason: "refusal"`
- You'll receive a 200 status code
- You'll be billed for the tokens generated
- The output may not match your schema because the refusal message takes precedence over schema constraints

**Token limit reached** (`stop_reason: "max_tokens"`)

If the response is cut off due to reaching the `max_tokens` limit:

- The response has `stop_reason: "max_tokens"`
- The output may be incomplete and not match your schema
- Retry with a higher `max_tokens` value to get the complete structured output

### Schema complexity limits

Structured outputs work by compiling your JSON schemas into a grammar that constrains Claude's output. More complex schemas produce larger grammars that take longer to compile. To protect against excessive compilation times, the API enforces several complexity limits.

#### Explicit limits

The following limits apply to all requests with `output_config.format` or `strict: true`:

| Limit | Value | Description |
|-------|-------|-------------|
| Strict tools per request | 20 | Maximum number of tools with `strict: true`. Non-strict tools don't count toward this limit. |
| Optional parameters | 24 | Total optional parameters across all strict tool schemas and JSON output schemas. Each parameter not listed in `required` counts toward this limit. |
| Parameters with union types | 16 | Total parameters that use `anyOf` or type arrays (e.g., `"type": ["string", "null"]`) across all strict schemas. These are especially expensive because they create exponential compilation cost. |

<Note>
These limits apply to the combined total across all strict schemas in a single request. For example, if you have 4 strict tools with 6 optional parameters each, you'll reach the 24-parameter limit even though no single tool seems complex.
</Note>

#### Additional internal limits

Beyond the explicit limits above, there are additional internal limits on the compiled grammar size. These limits exist because schema complexity doesn't reduce to a single dimension: features like optional parameters, union types, nested objects, and number of tools interact with each other in ways that can make the compiled grammar disproportionately large.

When these limits are exceeded, you'll receive a 400 error with the message "Schema is too complex for compilation." These errors mean the combined complexity of your schemas exceeds what can be efficiently compiled, even if each individual limit above is satisfied. As a final stop-gap, the API also enforces a **compilation timeout of 180 seconds**. Schemas that pass all explicit checks but produce very large compiled grammars may hit this timeout.

#### Tips for reducing schema complexity

If you're hitting complexity limits, try these strategies in order:

1. **Mark only critical tools as strict.** If you have many tools, reserve it for tools where schema violations cause real problems, and rely on Claude's natural adherence for simpler tools.

2. **Reduce optional parameters.** Make parameters `required` where possible. Each optional parameter roughly doubles a portion of the grammar's state space. If a parameter always has a reasonable default, consider making it required and having Claude provide that default explicitly.

3. **Simplify nested structures.** Deeply nested objects with optional fields compound the complexity. Flatten structures where possible.

4. **Split into multiple requests.** If you have many strict tools, consider splitting them across separate requests or sub-agents.

For persistent issues with valid schemas, [contact support](https://support.claude.com/en/articles/9015913-how-to-get-support) with your schema definition.

## Feature compatibility

**Works with:**
- **[Batch processing](/docs/en/build-with-claude/batch-processing)**: Process structured outputs at scale with 50% discount
- **[Token counting](/docs/en/build-with-claude/token-counting)**: Count tokens without compilation
- **[Streaming](/docs/en/build-with-claude/streaming)**: Stream structured outputs like normal responses
- **Combined usage**: Use JSON outputs (`output_config.format`) and strict tool use (`strict: true`) together in the same request

**Incompatible with:**
- **[Citations](/docs/en/build-with-claude/citations)**: Citations require interleaving citation blocks with text, which conflicts with strict JSON schema constraints. Returns 400 error if citations enabled with `output_config.format`.
- **Message Prefilling**: Incompatible with JSON outputs

<Tip>
**Grammar scope**: Grammars apply only to Claude's direct output, not to tool use calls, tool results, or thinking tags (when using [Extended Thinking](/docs/en/build-with-claude/extended-thinking)). Grammar state resets between sections, allowing Claude to think freely while still producing structured output in the final response.
</Tip>

# Gemini API
You can configure Gemini models to generate responses that adhere to a provided JSON
Schema. This ensures predictable, type-safe results and simplifies extracting
structured data from unstructured text.

Using structured outputs is ideal for:

- **Data extraction:** Pull specific information like names and dates from text.
- **Structured classification:** Classify text into predefined categories.
- **Agentic workflows:** Generate structured inputs for tools or APIs.

In addition to supporting JSON Schema in the REST API, the Google GenAI SDKs
make it easy to define schemas using
[Pydantic](https://docs.pydantic.dev/latest/) (Python) and
[Zod](https://zod.dev/) (JavaScript).

<button value="recipe" default="">Recipe Extractor</button> <button value="feedback">Content Moderation</button> <button value="recursive">Recursive Structures</button>

This example demonstrates how to extract structured data from text using basic
JSON Schema types like `object`, `array`, `string`, and `integer`.

### Python

    from google import genai
    from pydantic import BaseModel, Field
    from typing import List, Optional

    class Ingredient(BaseModel):
        name: str = Field(description="Name of the ingredient.")
        quantity: str = Field(description="Quantity of the ingredient, including units.")

    class Recipe(BaseModel):
        recipe_name: str = Field(description="The name of the recipe.")
        prep_time_minutes: Optional[int] = Field(description="Optional time in minutes to prepare the recipe.")
        ingredients: List[Ingredient]
        instructions: List[str]

    client = genai.Client()

    prompt = """
    Please extract the recipe from the following text.
    The user wants to make delicious chocolate chip cookies.
    They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,
    1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,
    3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.
    For the best part, they'll need 2 cups of semisweet chocolate chips.
    First, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,
    baking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar
    until light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry
    ingredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons
    onto ungreased baking sheets and bake for 9 to 11 minutes.
    """

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": Recipe.model_json_schema(),
        },
    )

    recipe = Recipe.model_validate_json(response.text)
    print(recipe)

### JavaScript

    import { GoogleGenAI } from "@google/genai";
    import { z } from "zod";
    import { zodToJsonSchema } from "zod-to-json-schema";

    const ingredientSchema = z.object({
      name: z.string().describe("Name of the ingredient."),
      quantity: z.string().describe("Quantity of the ingredient, including units."),
    });

    const recipeSchema = z.object({
      recipe_name: z.string().describe("The name of the recipe."),
      prep_time_minutes: z.number().optional().describe("Optional time in minutes to prepare the recipe."),
      ingredients: z.array(ingredientSchema),
      instructions: z.array(z.string()),
    });

    const ai = new GoogleGenAI({});

    const prompt = `
    Please extract the recipe from the following text.
    The user wants to make delicious chocolate chip cookies.
    They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,
    1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,
    3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.
    For the best part, they'll need 2 cups of semisweet chocolate chips.
    First, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,
    baking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar
    until light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry
    ingredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons
    onto ungreased baking sheets and bake for 9 to 11 minutes.
    `;

    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseJsonSchema: zodToJsonSchema(recipeSchema),
      },
    });

    const recipe = recipeSchema.parse(JSON.parse(response.text));
    console.log(recipe);

### Go

    package main

    import (
        "context"
        "fmt"
        "log"

        "google.golang.org/genai"
    )

    func main() {
        ctx := context.Background()
        client, err := genai.NewClient(ctx, nil)
        if err != nil {
            log.Fatal(err)
        }

        prompt := `
      Please extract the recipe from the following text.
      The user wants to make delicious chocolate chip cookies.
      They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,
      1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,
      3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.
      For the best part, they'll need 2 cups of semisweet chocolate chips.
      First, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,
      baking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar
      until light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry
      ingredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons
      onto ungreased baking sheets and bake for 9 to 11 minutes.
      `
        config := &genai.GenerateContentConfig{
            ResponseMIMEType: "application/json",
            ResponseJsonSchema: map[string]any{
                "type": "object",
                "properties": map[string]any{
                    "recipe_name": map[string]any{
                        "type":        "string",
                        "description": "The name of the recipe.",
                    },
                    "prep_time_minutes": map[string]any{
                        "type":        "integer",
                        "description": "Optional time in minutes to prepare the recipe.",
                    },
                    "ingredients": map[string]any{
                        "type": "array",
                        "items": map[string]any{
                            "type": "object",
                            "properties": map[string]any{
                                "name": map[string]any{
                                    "type":        "string",
                                    "description": "Name of the ingredient.",
                                },
                                "quantity": map[string]any{
                                    "type":        "string",
                                    "description": "Quantity of the ingredient, including units.",
                                },
                            },
                            "required": []string{"name", "quantity"},
                        },
                    },
                    "instructions": map[string]any{
                        "type":  "array",
                        "items": map[string]any{"type": "string"},
                    },
                },
                "required": []string{"recipe_name", "ingredients", "instructions"},
            },
        }

        result, err := client.Models.GenerateContent(
            ctx,
            "gemini-3-flash-preview",
            genai.Text(prompt),
            config,
        )
        if err != nil {
            log.Fatal(err)
        }
        fmt.Println(result.Text())
    }

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
        -H "x-goog-api-key: $GEMINI_API_KEY" \
        -H 'Content-Type: application/json' \
        -X POST \
        -d '{
          "contents": [{
            "parts":[
              { "text": "Please extract the recipe from the following text.\nThe user wants to make delicious chocolate chip cookies.\nThey need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,\n1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,\n3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.\nFor the best part, they will need 2 cups of semisweet chocolate chips.\nFirst, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,\nbaking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar\nuntil light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry\ningredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons\nonto ungreased baking sheets and bake for 9 to 11 minutes." }
            ]
          }],
          "generationConfig": {
            "responseMimeType": "application/json",
            "responseJsonSchema": {
              "type": "object",
              "properties": {
                "recipe_name": {
                  "type": "string",
                  "description": "The name of the recipe."
                },
                "prep_time_minutes": {
                    "type": "integer",
                    "description": "Optional time in minutes to prepare the recipe."
                },
                "ingredients": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "name": { "type": "string", "description": "Name of the ingredient."},
                      "quantity": { "type": "string", "description": "Quantity of the ingredient, including units."}
                    },
                    "required": ["name", "quantity"]
                  }
                },
                "instructions": {
                  "type": "array",
                  "items": { "type": "string" }
                }
              },
              "required": ["recipe_name", "ingredients", "instructions"]
            }
          }
        }'

**Example Response:**

    {
      "recipe_name": "Delicious Chocolate Chip Cookies",
      "ingredients": [
        {
          "name": "all-purpose flour",
          "quantity": "2 and 1/4 cups"
        },
        {
          "name": "baking soda",
          "quantity": "1 teaspoon"
        },
        {
          "name": "salt",
          "quantity": "1 teaspoon"
        },
        {
          "name": "unsalted butter (softened)",
          "quantity": "1 cup"
        },
        {
          "name": "granulated sugar",
          "quantity": "3/4 cup"
        },
        {
          "name": "packed brown sugar",
          "quantity": "3/4 cup"
        },
        {
          "name": "vanilla extract",
          "quantity": "1 teaspoon"
        },
        {
          "name": "large eggs",
          "quantity": "2"
        },
        {
          "name": "semisweet chocolate chips",
          "quantity": "2 cups"
        }
      ],
      "instructions": [
        "Preheat the oven to 375°F (190°C).",
        "In a small bowl, whisk together the flour, baking soda, and salt.",
        "In a large bowl, cream together the butter, granulated sugar, and brown sugar until light and fluffy.",
        "Beat in the vanilla and eggs, one at a time.",
        "Gradually beat in the dry ingredients until just combined.",
        "Stir in the chocolate chips.",
        "Drop by rounded tablespoons onto ungreased baking sheets and bake for 9 to 11 minutes."
      ]
    }

## Streaming

You can stream structured outputs, which allows you to start processing the
response as it's being generated, without having to wait for the entire output
to be complete. This can improve the perceived performance of your application.

The streamed chunks will be valid partial JSON strings, which can be
concatenated to form the final, complete JSON object.

### Python

    from google import genai
    from pydantic import BaseModel, Field
    from typing import Literal

    class Feedback(BaseModel):
        sentiment: Literal["positive", "neutral", "negative"]
        summary: str

    client = genai.Client()
    prompt = "The new UI is incredibly intuitive and visually appealing. Great job. Add a very long summary to test streaming!"

    response_stream = client.models.generate_content_stream(
        model="gemini-3-flash-preview",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": Feedback.model_json_schema(),
        },
    )

    for chunk in response_stream:
        print(chunk.candidates[0].content.parts[0].text)

### JavaScript

    import { GoogleGenAI } from "@google/genai";
    import { z } from "zod";
    import { zodToJsonSchema } from "zod-to-json-schema";

    const ai = new GoogleGenAI({});
    const prompt = "The new UI is incredibly intuitive and visually appealing. Great job! Add a very long summary to test streaming!";

    const feedbackSchema = z.object({
      sentiment: z.enum(["positive", "neutral", "negative"]),
      summary: z.string(),
    });

    const stream = await ai.models.generateContentStream({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseJsonSchema: zodToJsonSchema(feedbackSchema),
      },
    });

    for await (const chunk of stream) {
      console.log(chunk.candidates[0].content.parts[0].text)
    }

## Structured outputs with tools

> [!WARNING]
> **Preview:** This feature is available only to Gemini 3 series models, `gemini-3.1-pro-preview` and `gemini-3-flash-preview`.

Gemini 3 lets you combine Structured Outputs with built-in tools, including
[Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search),
[URL Context](https://ai.google.dev/gemini-api/docs/url-context),
[Code Execution](https://ai.google.dev/gemini-api/docs/code-execution),
[File Search](https://ai.google.dev/gemini-api/docs/file-search#structured-output), and
[Function Calling](https://ai.google.dev/gemini-api/docs/function-calling).

### Python

    from google import genai
    from pydantic import BaseModel, Field
    from typing import List

    class MatchResult(BaseModel):
        winner: str = Field(description="The name of the winner.")
        final_match_score: str = Field(description="The final match score.")
        scorers: List[str] = Field(description="The name of the scorer.")

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents="Search for all details for the latest Euro.",
        config={
            "tools": [
                {"google_search": {}},
                {"url_context": {}}
            ],
            "response_mime_type": "application/json",
            "response_json_schema": MatchResult.model_json_schema(),
        },  
    )

    result = MatchResult.model_validate_json(response.text)
    print(result)

### JavaScript

    import { GoogleGenAI } from "@google/genai";
    import { z } from "zod";
    import { zodToJsonSchema } from "zod-to-json-schema";

    const ai = new GoogleGenAI({});

    const matchSchema = z.object({
      winner: z.string().describe("The name of the winner."),
      final_match_score: z.string().describe("The final score."),
      scorers: z.array(z.string()).describe("The name of the scorer.")
    });

    async function run() {
      const response = await ai.models.generateContent({
        model: "gemini-3.1-pro-preview",
        contents: "Search for all details for the latest Euro.",
        config: {
          tools: [
            { googleSearch: {} },
            { urlContext: {} }
          ],
          responseMimeType: "application/json",
          responseJsonSchema: zodToJsonSchema(matchSchema),
        },
      });

      const match = matchSchema.parse(JSON.parse(response.text));
      console.log(match);
    }

    run();

### REST

    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent" \
      -H "x-goog-api-key: $GEMINI_API_KEY" \
      -H 'Content-Type: application/json' \
      -X POST \
      -d '{
        "contents": [{
          "parts": [{"text": "Search for all details for the latest Euro."}]
        }],
        "tools": [
          {"googleSearch": {}},
          {"urlContext": {}}
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseJsonSchema": {
                "type": "object",
                "properties": {
                    "winner": {"type": "string", "description": "The name of the winner."},
                    "final_match_score": {"type": "string", "description": "The final score."},
                    "scorers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The name of the scorer."
                    }
                },
                "required": ["winner", "final_match_score", "scorers"]
            }
        }
      }'

## JSON schema support

To generate a JSON object, set the `response_mime_type` in the generation configuration to `application/json` and provide a `response_json_schema`. The schema must be a valid [JSON Schema](https://json-schema.org/) that describes the desired output format.

The model will then generate a response that is a syntactically valid JSON string matching the provided schema. When using structured outputs, the model will produce outputs in the same order as the keys in the schema.

Gemini's structured output mode supports a subset of the [JSON Schema](https://json-schema.org) specification.

The following values of `type` are supported:

- **`string`**: For text.
- **`number`**: For floating-point numbers.
- **`integer`**: For whole numbers.
- **`boolean`**: For true/false values.
- **`object`**: For structured data with key-value pairs.
- **`array`**: For lists of items.
- **`null`** : To allow a property to be null, include `"null"` in the type array (e.g., `{"type": ["string", "null"]}`).

These descriptive properties help guide the model:

- **`title`**: A short description of a property.
- **`description`**: A longer and more detailed description of a property.

### Type-specific properties

**For `object` values:**

- **`properties`**: An object where each key is a property name and each value is a schema for that property.
- **`required`**: An array of strings, listing which properties are mandatory.
- **`additionalProperties`** : Controls whether properties not listed in `properties` are allowed. Can be a boolean or a schema.

**For `string` values:**

- **`enum`**: Lists a specific set of possible strings for classification tasks.
- **`format`** : Specifies a syntax for the string, such as `date-time`, `date`, `time`.

**For `number` and `integer` values:**

- **`enum`**: Lists a specific set of possible numeric values.
- **`minimum`**: The minimum inclusive value.
- **`maximum`**: The maximum inclusive value.

**For `array` values:**

- **`items`**: Defines the schema for all items in the array.
- **`prefixItems`**: Defines a list of schemas for the first N items, allowing for tuple-like structures.
- **`minItems`**: The minimum number of items in the array.
- **`maxItems`**: The maximum number of items in the array.

## Model support

The following models support structured output:

| Model | Structured Outputs |
|---|---|
| Gemini 3.1 Pro Preview | ✔️ |
| Gemini 3 Flash Preview | ✔️ |
| Gemini 2.5 Pro | ✔️ |
| Gemini 2.5 Flash | ✔️ |
| Gemini 2.5 Flash-Lite | ✔️ |
| Gemini 2.0 Flash | ✔️\* |
| Gemini 2.0 Flash-Lite | ✔️\* |

*\* Note that Gemini 2.0 requires an explicit `propertyOrdering` list within the JSON input to define the preferred structure. You can find an example in this [cookbook](https://github.com/google-gemini/cookbook/blob/main/examples/Pdf_structured_outputs_on_invoices_and_forms.ipynb).*

## Structured outputs vs. function calling

Both structured outputs and function calling use JSON schemas, but they serve different purposes:

| Feature | Primary Use Case |
|---|---|
| **Structured Outputs** | **Formatting the final response to the user.** Use this when you want the model's *answer* to be in a specific format (e.g., extracting data from a document to save to a database). |
| **Function Calling** | **Taking action during the conversation.** Use this when the model needs to *ask you* to perform a task (e.g., "get current weather") before it can provide a final answer. |

## Best practices

- **Clear descriptions:** Use the `description` field in your schema to provide clear instructions to the model about what each property represents. This is crucial for guiding the model's output.
- **Strong typing:** Use specific types (`integer`, `string`, `enum`) whenever possible. If a parameter has a limited set of valid values, use an `enum`.
- **Prompt engineering:** Clearly state in your prompt what you want the model to do. For example, "Extract the following information from the text..." or "Classify this feedback according to the provided schema...".
- **Validation:** While structured output guarantees syntactically correct JSON, it does not guarantee the values are semantically correct. Always validate the final output in your application code before using it.
- **Error handling:** Implement robust error handling in your application to gracefully manage cases where the model's output, while schema-compliant, may not meet your business logic requirements.

## Limitations

- **Schema subset:** Not all features of the JSON Schema specification are supported. The model ignores unsupported properties.
- **Schema complexity:** The API may reject very large or deeply nested schemas. If you encounter errors, try simplifying your schema by shortening property names, reducing nesting, or limiting the number of constraints.