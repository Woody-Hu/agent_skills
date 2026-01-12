---
name: mermaid-sequence
description: "Sequence diagram creation and editing. When Claude needs to create or modify sequence diagrams, interaction diagrams, or message flow diagrams using Mermaid syntax"
license: Proprietary
---

# Mermaid Sequence Diagram Creation and Editing

## Overview

This skill enables creating and editing sequence diagrams, interaction diagrams, and message flow diagrams using Mermaid syntax. Sequence diagrams show how objects interact in a given scenario, focusing on the order of message exchange.

## When to Use This Skill

Use this skill when you need to:
- Document API interactions
- Visualize system communication flows
- Design protocol handshakes
- Map out request/response cycles
- Document authentication flows
- Design error handling scenarios
- Visualize async/sync operations

## Mermaid Sequence Diagram Syntax

### Basic Structure

```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob

    A->>B: Hello Bob, how are you?
    B-->>A: I am good thanks!
```

### Participants

```mermaid
sequenceDiagram
    actor User
    participant Server
    participant Database as DB
    participant API as External API

    User->>Server: Request
    Server->>Database: Query
    Database-->>Server: Result
    Server->>API: External Call
    API-->>Server: Response
    Server-->>User: Final Response
```

### Message Types

```mermaid
sequenceDiagram
    participant A
    participant B
    participant C

    A->>B: Synchronous message (solid line, filled arrow)
    B-->>A: Return message (dashed line, open arrow)
    A->>C: Asynchronous message (open arrow)
    C-->>B: Dashed return (dashed line, open arrow)
    A-xB: Lost message (cross)
    B--xA: Found message (cross)
```

### Self-Calls and Loops

```mermaid
sequenceDiagram
    participant Service
    participant Database

    Service->>Service: Internal validation
    Service->>Database: Query data

    loop Retry logic
        Database-->>Service: Partial result
        Service->>Service: Process batch
    end

    Database-->>Service: Complete result
```

### Alt and Opt Blocks

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Database

    Client->>Server: Request
    Server->>Database: Query

    alt Data found
        Database-->>Server: Data
        Server-->>Client: Success response
    else Data not found
        Database-->>Server: Null
        Server-->>Client: 404 Not Found
    end

    opt Optional logging
        Server->>Server: Log request
    end
```

### Par and Critical Sections

```mermaid
sequenceDiagram
    participant Client
    participant ServiceA
    participant ServiceB
    participant Database

    Client->>ServiceA: Request
    Client->>ServiceB: Request

    par Parallel processing
        ServiceA->>Database: Query A
        ServiceB->>Database: Query B
    end

    Database-->>ServiceA: Result A
    Database-->>ServiceB: Result B

    ServiceA-->>Client: Response A
    ServiceB-->>Client: Response B
```

### Notes and Comments

```mermaid
sequenceDiagram
    participant User
    participant System

    Note over User, System: Authentication Flow
    User->>System: Login request

    Note right of System: Validate credentials
    System->>System: Check database

    alt Valid credentials
        System-->>User: Success
    else Invalid credentials
        System-->>User: Error
    end

    Note left of User: User receives response
```

## Common Sequence Diagram Patterns

### REST API Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant LoadBalancer
    participant APIGateway
    participant Service
    participant Database

    Client->>LoadBalancer: HTTPS Request
    LoadBalancer->>APIGateway: Forward request
    APIGateway->>APIGateway: Authentication
    APIGateway->>APIGateway: Rate limiting
    APIGateway->>Service: Forward to service
    Service->>Database: Query data
    Database-->>Service: Data
    Service-->>APIGateway: Response
    APIGateway-->>LoadBalancer: Response
    LoadBalancer-->>Client: HTTPS Response
```

### Authentication Flow (OAuth2)

```mermaid
sequenceDiagram
    participant User
    participant ClientApp
    participant AuthServer
    participant ResourceServer

    User->>ClientApp: Click login
    ClientApp->>AuthServer: Redirect to auth endpoint
    AuthServer-->>ClientApp: Login page
    User->>AuthServer: Enter credentials
    AuthServer->>AuthServer: Validate credentials
    AuthServer-->>ClientApp: Authorization code
    ClientApp->>AuthServer: Exchange code for token
    AuthServer-->>ClientApp: Access token
    ClientApp->>ResourceServer: Request with token
    ResourceServer->>ResourceServer: Validate token
    ResourceServer-->>ClientApp: Protected resource
```

### Database Transaction Flow

```mermaid
sequenceDiagram
    participant Application
    participant TransactionManager
    participant Database
    participant Log

    Application->>TransactionManager: Begin transaction
    TransactionManager->>Database: START TRANSACTION
    Database-->>TransactionManager: OK

    Application->>TransactionManager: Execute operations
    TransactionManager->>Database: INSERT/UPDATE/DELETE
    Database-->>TransactionManager: Result

    alt Success
        TransactionManager->>Database: COMMIT
        Database-->>TransactionManager: OK
        TransactionManager->>Log: Log success
        TransactionManager-->>Application: Success
    else Failure
        TransactionManager->>Database: ROLLBACK
        Database-->>TransactionManager: OK
        TransactionManager->>Log: Log error
        TransactionManager-->>Application: Error
    end
```

### Message Queue Processing

```mermaid
sequenceDiagram
    participant Producer
    participant Queue
    participant Consumer
    participant Database

    Producer->>Queue: Publish message
    Queue->>Queue: Store message

    loop Poll for messages
        Consumer->>Queue: Get message
        Queue-->>Consumer: Message
        Consumer->>Consumer: Process message

        alt Processing successful
            Consumer->>Database: Save result
            Database-->>Consumer: OK
            Consumer->>Queue: Acknowledge
            Queue->>Queue: Remove message
        else Processing failed
            Consumer->>Queue: Negative acknowledge
            Queue->>Queue: Requeue message
        end
    end
```

### WebSocket Communication

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Service
    participant Database

    Client->>Server: WebSocket upgrade request
    Server->>Service: Validate connection
    Service-->>Server: OK
    Server-->>Client: Connection established

    loop Message exchange
        Client->>Server: Send message
        Server->>Service: Process message
        Service->>Database: Query/update
        Database-->>Service: Result
        Service-->>Server: Response
        Server-->>Client: Send response
    end

    Client->>Server: Close connection
    Server-->>Client: Connection closed
```

### Error Handling Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant Database
    participant Logger

    Client->>API: Request
    API->>Service: Forward request

    alt Service available
        Service->>Database: Query
        Database-->>Service: Data
        Service-->>API: Response
        API-->>Client: 200 OK
    else Service unavailable
        Service-->>API: 503 Service Unavailable
        API->>Logger: Log error
        API-->>Client: 503 Service Unavailable
    else Database error
        Service->>Database: Query
        Database-->>Service: Error
        Service->>Logger: Log error
        Service-->>API: 500 Internal Server Error
        API-->>Client: 500 Internal Server Error
    end
```

### Async Event Processing

```mermaid
sequenceDiagram
    participant User
    participant API
    participant EventBus
    participant Handler1
    participant Handler2
    participant Database

    User->>API: Trigger action
    API->>Database: Save initial state
    Database-->>API: OK
    API->>EventBus: Publish event
    API-->>User: 202 Accepted

    par Event handlers
        EventBus->>Handler1: Event
        Handler1->>Database: Update data
        Database-->>Handler1: OK
        Handler1->>EventBus: Acknowledge
    and
        EventBus->>Handler2: Event
        Handler2->>Handler2: Process
        Handler2->>Database: Log
        Database-->>Handler2: OK
        Handler2->>EventBus: Acknowledge
    end
```

## Styling and Customization

### Participant Styling

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User
    participant Client as 📱 Client
    participant Server as 🖥️ Server
    participant Database as 🗄️ Database

    User->>Client: Action
    Client->>Server: Request
    Server->>Database: Query
    Database-->>Server: Data
    Server-->>Client: Response
    Client-->>User: Result
```

### Activation Boxes

```mermaid
sequenceDiagram
    participant A
    participant B
    participant C

    A->>B: Request
    activate B
    B->>C: Forward
    activate C
    C-->>B: Response
    deactivate C
    B-->>A: Result
    deactivate B
```

### Box and Rect

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database

    box Frontend Layer
        participant Frontend
    end

    box Backend Layer
        participant Backend
        participant Database
    end

    User->>Frontend: Request
    Frontend->>Backend: API Call
    Backend->>Database: Query
    Database-->>Backend: Data
    Backend-->>Frontend: Response
    Frontend-->>User: Result
```

## Best Practices

### Design Principles

1. **Clear participants**: Use descriptive names for all participants
2. **Logical flow**: Arrange participants left-to-right in order of interaction
3. **Appropriate detail**: Include only relevant messages and steps
4. **Consistent naming**: Use consistent naming conventions
5. **Error handling**: Include alt/opt blocks for error scenarios

### Message Naming

- Use verb-noun format: `getUserData`, `updateRecord`
- Be descriptive but concise: `validateCredentials` not `checkIfTheUserCredentialsAreValid`
- Include response status in returns: `returnSuccess`, `returnError`

### When to Use Each Message Type

- `->>`: Synchronous request (wait for response)
- `-->`: Asynchronous message (fire and forget)
- `-->>`: Return message (response to synchronous request)
- `->`: Direct message (no response expected)
- `--`: Return message (no arrowhead)

### Organization Tips

- Use `autonumber` for complex diagrams
- Group related operations with `loop`, `alt`, `opt`
- Use `par` for concurrent operations
- Add notes to explain complex sections
- Use `box` to group related participants

## Workflow

1. **Identify participants**: List all systems/objects involved
2. **Determine interactions**: Map out message exchanges
3. **Choose message types**: Select appropriate arrow styles
4. **Add control structures**: Use alt/opt/par/loop as needed
5. **Add annotations**: Include notes for clarity
6. **Review and refine**: Check for completeness and clarity
7. **Validate**: Ensure diagram accurately represents the flow

## Rendering

To render Mermaid sequence diagrams:
- Use the Mermaid Live Editor: https://mermaid.live
- Use Mermaid CLI: `mmdc -i input.mmd -o output.png`
- Integrate with documentation tools (GitHub, GitLab, Notion, etc.)

## Common Issues and Solutions

### Diagram Too Wide
- Reduce number of participants
- Use shorter participant names
- Consider breaking into multiple diagrams

### Too Many Messages
- Group related messages
- Use sub-diagrams for complex flows
- Hide implementation details

### Confusing Flow
- Add autonumbering
- Use notes to explain sections
- Simplify message names
- Break into multiple diagrams

### Missing Error Handling
- Add alt blocks for error cases
- Include timeout scenarios
- Document retry logic

## Dependencies

Required tools:
- **Mermaid CLI**: `npm install -g @mermaid-js/mermaid-cli`
- **Node.js**: Required for Mermaid CLI
