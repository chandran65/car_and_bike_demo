# Documentation

This folder contains comprehensive documentation for the Mahindra Bot project, organized by category.

## 📁 Documentation Structure

### 🔧 Services (`services/`)
Documentation for core services and components:

- **[Car Service](services/car-service.md)** - Car data management, search, filtering, and comparison
- **[FAQ Service](services/faq-service.md)** - Semantic FAQ search using OpenAI embeddings
- **[Mahindra Bot Core](services/mahindra-bot-core.md)** - Complete AI agent system with intent classification and skills

### 📖 Guides (`guides/`)
Quick start guides and tutorials:

- **[FAQ Quick Start](guides/faq-quick-start.md)** - 30-second guide to using the FAQ service

### 📊 Data (`data/`)
Data structure and content documentation:

- **[Consolidated FAQs](data/consolidated-faqs.md)** - FAQ database structure (366 FAQs across 5 categories)

### 🔄 Updates (`updates/`)
Feature updates and migration notes:

- **[Error Handling Update](updates/error-handling-update.md)** - Enhanced error handling with fuzzy matching
- **[Serialization Update](updates/serialization-update.md)** - Human-readable serialization format
- **[Demo Migration](updates/demo-migration.md)** - Moving demos to dedicated folder
- **[LLM Service Refactor](updates/llm-service-refactor.md)** - Refactoring LLM service into modular package

### 📋 Planning (`planning/`)
Architecture and design documents:

- **[Mahindra Bot Core Plan](planning/mahindra-bot-core-plan.md)** - Complete implementation plan and architecture

### ✅ Implementation (`implementation/`)
Implementation summaries and delivery reports:

- **[Mahindra Bot Core Complete](implementation/mahindra-bot-core-complete.md)** - Implementation completion summary
- **[FAQ Service Implementation](implementation/faq-service-implementation.md)** - FAQ service implementation details
- **[Delivery Summary](implementation/delivery-summary.md)** - Complete project delivery report
- **[FAQ Service Demo Results](implementation/faq-service-demo-results.md)** - Demo execution results

---

## 🚀 Quick Navigation

### For New Users
1. Start with the main [README](../README.md) in the project root
2. Read the [FAQ Quick Start Guide](guides/faq-quick-start.md)
3. Explore service documentation in the [services/](services/) folder

### For Developers
1. Check [Planning](planning/) for architecture and design
2. Read [Implementation](implementation/) summaries for technical details
3. Review [Updates](updates/) for recent changes

### For Integration
1. **Car Service**: See [services/car-service.md](services/car-service.md)
2. **FAQ Search**: See [services/faq-service.md](services/faq-service.md)
3. **Bot Agent**: See [services/mahindra-bot-core.md](services/mahindra-bot-core.md)

---

## 📝 Documentation Standards

All documentation follows these principles:
- **Clear examples** with code snippets
- **Practical usage** guides
- **Complete API** references
- **Troubleshooting** sections
- **Performance** metrics where applicable

---

## 🔗 Related Resources

- **Demos**: See [demos/README.md](../demos/README.md) for demonstration scripts
- **Tests**: Check `tests/` folder for test suites
- **Source Code**: Browse `src/mahindrabot/` for implementation

---

## 📦 Project Components

### Core Services
- **CarService** - 260 cars loaded, 137 tests passing
- **FAQService** - 329 FAQs indexed, 18 tests passing
- **LLM Service** - Modular service with streaming and tool calling
- **Mahindra Bot Core** - Complete agent system with 4 intent types

### Features
- ✅ Semantic search with OpenAI embeddings
- ✅ Intent classification and skill routing
- ✅ Error handling with fuzzy matching
- ✅ Streaming responses
- ✅ Tool calling and function execution
- ✅ OTP-based booking flow
- ✅ Comprehensive test coverage

---

**Last Updated**: December 14, 2024
