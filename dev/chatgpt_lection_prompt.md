# OpenLingu Lection Content Generation Guide

## Overview
This document provides guidelines for generating lection content in JSON format for the OpenLingu language learning platform. The content should be educational, engaging, and properly structured for the platform's widget system.

## Lection Structure

```json
{
  "id": "unique_lection_id",
  "title": "Lection Title",
  "description": "Brief description of the lection",
  "language": "language_code (e.g., 'es', 'fr', 'de')",
  "difficulty": "beginner|intermediate|advanced",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "pages": []
}
```

## Page Structure

Each page contains:
- `title`: The page title
- `description`: A brief description of the page content
- `widgets`: An array of widget objects

## Available Widgets

### 1. Text Widget
For displaying regular text content.

```json
{
  "type": "text",
  "data": {
    "text": "Your text here",
    "size": 16,
    "weight": "normal|bold",
    "color": "#000000"
  }
}
```

### 2. Underlined Text Widget
For highlighting specific words in a text.

```json
{
  "type": "underlined_text",
  "data": {
    "text": "This is a sample text with important words",
    "underlined": {
      "0": "#FF0000",  // First word (index 0)
      "3": "#0000FF"   // Fourth word (index 3)
    },
    "font_size": 16,
    "bgcolor": "#F5F5F5"
  }
}
```

### 3. Matchable Pairs
For creating matching exercises.

```json
{
  "type": "matchable_pairs",
  "data": {
    "left_items": ["Hola", "Gracias"],
    "right_items": ["Hello", "Thank you"]
  }
}
```

### 4. Draggable Text
For fill-in-the-blank exercises with draggable options.

```json
{
  "type": "draggable_text",
  "data": {
    "text": "The cat sat on the mat.",
    "gaps_idx": [1, 4],
    "options": {
      "quick": 0,
      "brown": 0,
      "floor": 1,
      "bed": 1
    }
  }
}
```

## Draggable Text Indexing System

### How the Draggable Text Widget Works:

1. **Text Splitting**:
   - The input text is split into words using spaces as delimiters
   - Each space between words is assigned an index starting from 0
   - For the example "The cat sat on the mat.":
     ```
     Index 0: [start]The
     Index 1: The[ ]cat
     Index 2: cat[ ]sat
     Index 3: sat[ ]on
     Index 4: on[ ]the
     Index 5: the[ ]mat.
     ```

2. **gaps_idx**:
   - Defines where gaps should be created in the text
   - Each number in the array corresponds to a space index
   - In the example: `[1, 4]` means:
     - Create a gap at space index 1 (after "The")
     - Create a gap at space index 4 (after "on")

3. **options**:
   - Maps words to the gap index where they can be placed
   - The format is `"word": gap_index`
   - In the example:
     - "quick" and "brown" can be placed in gap 0 (after "The")
     - "floor" and "bed" can be placed in gap 1 (after "on")

### Visual Representation:
```
The [gap 0] cat sat on [gap 1] the mat.
```
Where:
- [gap 0] can be filled with: "quick" or "brown"
- [gap 1] can be filled with: "floor" or "bed"

### Example Output:
- "The quick cat sat on the mat." (with "quick" in gap 0)
- "The brown cat sat on the floor." (with "brown" in gap 0 and "floor" in gap 1)

### Key Points:
- `gaps_idx` points to the spaces between words, not the words themselves
- The first space (before the first word) is index 0
- Each option word is mapped to a specific gap index
- Multiple options can be mapped to the same gap index to create multiple choice options for that gap

### Example

**Sentence:** "The quick brown fox jumps over the lazy dog."

| Word Index | Word  |
|------------|-------|
| 0          | The   |
| 1          | quick |
| 2          | brown |
| 3          | fox   |
| 4          | jumps |
| 5          | over  |
| 6          | the   |
| 7          | lazy  |
| 8          | dog.  |


### Gap Placement

To create gaps at specific word positions:
1. Identify the target word indices (0-based)
2. Add these indices to the `gaps_idx` array
3. The words at these indices will be replaced with draggable gaps

**Example:**
```json
{
  "text": "The quick brown fox jumps over the lazy dog.",
  "gaps_idx": [1, 3, 7],
  "options": {
    "quick": 0,
    "fast": 0,
    "fox": 1,
    "dog": 1,
    "lazy": 2,
    "sleepy": 2
  }
}
```

This will create gaps at words 1 ("quick"), 3 ("fox"), and 7 ("lazy").

## Content Guidelines

1. **Text Length**: Keep text concise and focused
2. **Difficulty Level**: Match the language complexity to the specified difficulty
3. **Instructions**: Include clear instructions for interactive elements
4. **Variety**: Use a mix of widget types for engagement
5. **Localization**: Ensure all content is culturally appropriate for the target language

## Example Lection

```json
{
  "id": "spanish_greetings_101",
  "title": "Basic Spanish Greetings",
  "description": "Learn common Spanish greetings and introductions",
  "language": "es",
  "difficulty": "beginner",
  "created_at": "2025-06-25T12:00:00+02:00",
  "updated_at": "2025-06-25T12:00:00+02:00",
  "pages": [
    {
      "title": "Greetings",
      "description": "Learn basic Spanish greetings",
      "widgets": [
        {
          "type": "text",
          "data": {
            "text": "Here are some common Spanish greetings:",
            "size": 16,
            "weight": "bold"
          }
        },
        {
          "type": "matchable_pairs",
          "data": {
            "left_items": ["Hola", "Buenos días", "Buenas tardes", "Buenas noches"],
            "right_items": ["Hello", "Good morning", "Good afternoon", "Good evening"]
          }
        },
        {
          "type": "draggable_text",
          "data": {
            "text": "Complete the conversation with the correct greetings:",
            "gaps_idx": [1, 4],
            "options": {
              "Hola": 0,
              "Buenos días": 0,
              "Buenas noches": 1,
              "Hasta mañana": 1
            }
          }
        }
      ]
    }
  ]
}
```

## Best Practices

1. **Widget Order**: Start with instruction text, then examples, followed by interactive exercises
2. **Progressive Difficulty**: Start simple and gradually increase complexity
3. **Feedback**: Ensure correct/incorrect answers provide learning value
4. **Accessibility**: Use clear, simple language and provide sufficient contrast
5. **Testing**: Always test the generated content to ensure all widgets function as expected
