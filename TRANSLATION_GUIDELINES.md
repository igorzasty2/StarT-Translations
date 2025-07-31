# Translation Guidelines for Contributors

## Core Principles

### 1. Human Translation Only
- **Never use** Google Translate, DeepL, or any automated translation tool
- **Never use** AI assistants (ChatGPT, etc.) for direct translation
- All translations must be created by humans who speak the language natively or fluently

### 2. Context Matters
- Understand what you're translating (items, quests, UI elements, etc.)
- Consider how the text will appear in-game
- Maintain the same tone and style as the original

### 3. Technical Accuracy
- Preserve all formatting codes (`§` codes)
- Keep placeholders intact (`%1$s`, `{0}`, etc.)
- Don't remove or modify technical elements

## Translation Process

### Before You Start
1. **Understand the modpack**: Play with the English version if possible
2. **Check existing translations**: Look for consistency patterns
3. **Set up your workspace**: Use the provided tools
4. **Create a backup**: Always backup before major changes

### During Translation
1. **Work in categories**: Complete one mod/category at a time
2. **Use the GUI tools**: Take advantage of formatting helpers
3. **Check your work**: Use the validation features
4. **Test formatting**: Preview Minecraft formatting codes
5. **Save frequently**: Don't lose your work

### After Translation
1. **Validate**: Run the built-in validation tools
2. **Review**: Check for consistency and accuracy
3. **Submit**: Follow the project's submission process

## Common Mistakes to Avoid

### ❌ Don't Do This:
- Copy English text as translation
- Use automated translation tools
- Remove formatting codes
- Change placeholder syntax
- Leave empty translations
- Use inconsistent terminology
- Ignore context and tone

### ✅ Do This Instead:
- Translate based on understanding
- Research proper terminology
- Preserve all formatting
- Keep placeholders unchanged
- Mark uncertain translations with [TODO]
- Create terminology glossaries
- Consider the gaming context

## Quality Standards

### Minimum Requirements
- [ ] No automated translation used
- [ ] All placeholders preserved
- [ ] Formatting codes maintained
- [ ] No empty translations
- [ ] Basic grammar and spelling correct

### Excellence Standards
- [ ] Contextually appropriate translation
- [ ] Consistent terminology
- [ ] Natural language flow
- [ ] Cultural adaptation where needed
- [ ] Tested in-game context
- [ ] Peer reviewed by native speaker

## Getting Help

### Red Flags
If you find yourself:
- Translating without understanding
- Using automated tools
- Copying other translations blindly
- Feeling rushed or pressured

**Stop and reassess your approach**

## Technical Reference

### Minecraft Formatting Codes
```
Colors:      §0-§f (black to white)
Formatting:  §l (bold), §o (italic), §n (underline)
Special:     §k (obfuscated), §m (strikethrough), §r (reset)
```

### Placeholder Types
```
Java style:  %1$s, %2$d, %3$f
C style:     {0}, {1}, {2}
Named:       {player}, {item}, {count}
```

### File Structure
```
lang/
  category/
    en_us.json    (source language)
    your_lang.json (your translations)
```

---

**Remember**: Good translation is an art that combines linguistic skill, cultural understanding, and technical precision. Take your time, do it right, and create translations that enhance the gaming experience for your language community.
