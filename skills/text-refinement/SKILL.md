---
name: text-refinement
description: Text refinement and rewriting tool that leverages reference writing styles to regenerate or polish files. When Claude needs to rewrite content to match a specific style, improve clarity, enhance professionalism, or adapt text to a particular audience based on reference samples.
license: Proprietary. LICENSE.txt has complete terms
---

# Text Refinement Guide

## Overview

This guide covers how to use reference writing styles to refine, rewrite, and polish text content across various file types. The text-refinement skill enables you to analyze reference text patterns and apply those patterns to target content for consistent, high-quality results.

## Core Concepts

### Style Matching

The text-refinement skill works by:
1. Analyzing reference text to identify writing patterns, tone, and structure
2. Comparing with target content to identify areas for improvement
3. Rewriting content to match the reference style while preserving original meaning

### Common Use Cases

- **Brand Voice Consistency**: Align content with company brand guidelines using reference materials
- **Academic Writing**: Convert casual text to formal academic style
- **Technical Documentation**: Improve clarity and precision based on reference documentation
- **Marketing Copy**: Enhance persuasive language using reference marketing materials
- **Cross-Platform Adaptation**: Rewrite content for different audiences or platforms

## Usage Workflow

### Step 1: Prepare Reference and Target Files

1. **Reference File**: Contains the desired writing style (e.g., brand guidelines, sample document)
2. **Target File**: Content that needs refinement (e.g., draft document, blog post)

### Step 2: Analyze Reference Style

```python
# Example: Analyze reference text style
with open("reference.txt", "r", encoding="utf-8") as f:
    reference_text = f.read()

# Identify key style elements manually or using analysis
# - Vocabulary complexity and tone
# - Sentence structure and length
# - Paragraph organization
# - Terminology and jargon usage
# - Punctuation and formatting preferences
```

### Step 3: Refine Target Content

```python
# Example: Refine target content using reference style
with open("target.txt", "r", encoding="utf-8") as f:
    target_text = f.read()

# Rewrite content to match reference style
# 1. Maintain original meaning and key information
# 2. Apply reference vocabulary and tone
# 3. Match sentence structure patterns
# 4. Follow reference formatting conventions

refined_text = """[Refined content matching reference style]"""

# Save refined content
with open("refined.txt", "w", encoding="utf-8") as f:
    f.write(refined_text)
```

## Detailed Examples

### Example 1: Brand Voice Alignment

**Reference Text (Brand Guidelines)**: "Our innovative solutions empower businesses to achieve sustainable growth through cutting-edge technology and customer-centric strategies."

**Target Text**: "We make tools that help companies grow by using new tech and focusing on customers."

**Refined Text**: "Our innovative solutions empower businesses to achieve sustainable growth through cutting-edge technology and customer-centric strategies."

### Example 2: Academic Writing Enhancement

**Reference Text (Academic Paper)**: "The empirical evidence suggests a significant correlation between regular exercise and improved cognitive function in elderly populations."

**Target Text**: "Studies show that old people who exercise a lot have better brain function."

**Refined Text**: "Empirical evidence indicates a significant correlation between consistent physical activity and enhanced cognitive performance in elderly demographics."

### Example 3: Technical Documentation Improvement

**Reference Text (Technical Manual)**: "To configure the network settings, navigate to the Administration panel, select Network Configuration from the sidebar menu, and enter the appropriate IP address, subnet mask, and gateway information in the designated fields."

**Target Text**: "Go to settings, find network stuff, and type in your IP, subnet, and gateway."

**Refined Text**: "To configure network settings, navigate to the Administration panel, select Network Configuration from the sidebar menu, and input the appropriate IP address, subnet mask, and gateway information in the designated fields."

## Best Practices

### Style Analysis Tips

1. **Vocabulary**: Identify common words, phrases, and terminology
2. **Sentence Structure**: Note average sentence length and complexity
3. **Tone**: Determine formality level, voice (active/passive), and emotional tone
4. **Organization**: Observe paragraph structure, headings, and flow
5. **Formatting**: Note punctuation, capitalization, and formatting preferences

### Rewriting Guidelines

1. **Preserve Meaning**: Never alter the original intent or key information
2. **Maintain Context**: Ensure refined content fits appropriately within its context
3. **Consistency**: Apply style changes uniformly throughout the document
4. **Clarity**: Prioritize readability while matching reference style
5. **Accuracy**: Verify technical terms and specialized language

## File Types Supported

The text-refinement skill works with various file types:
- Plain text files (.txt)
- Markdown files (.md)
- Documentation files (.rst, .adoc)
- Source code comments
- Configuration files
- Email templates
- Presentation scripts

## Limitations and Considerations

1. **Context Awareness**: Ensure reference and target content share similar context
2. **Technical Accuracy**: For specialized content, maintain technical correctness
3. **Cultural Nuances**: Be mindful of cultural references and idioms
4. **Legal Compliance**: Avoid altering legally binding language without proper review
5. **Originality**: Balance style matching with maintaining unique voice when appropriate

## Quality Assurance

### Review Process

1. **Compare with Original**: Verify all key information is preserved
2. **Check Style Consistency**: Ensure refined content matches reference style
3. **Readability Test**: Confirm content is clear and understandable
4. **Context Check**: Verify content fits appropriately within its intended context

### Example QA Checklist

- [ ] All factual information is preserved
- [ ] Writing style matches reference material
- [ ] Sentence structure is consistent with reference
- [ ] Vocabulary aligns with target audience
- [ ] Content flows logically and maintains coherence
- [ ] No grammatical or spelling errors

## Next Steps

1. Select appropriate reference materials that exemplify the desired style
2. Prepare target content for refinement
3. Apply the workflow outlined in this guide
4. Review refined content against quality assurance checklist
5. Iterate as needed to achieve desired results
