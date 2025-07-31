"""
Translation Manager - Core logic for managing Minecraft modpack translations
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class TranslationEntry:
    """Represents a single translation entry"""
    key: str
    category: str
    subcategory: str
    english_text: str
    translated_text: str = ""
    has_formatting: bool = False
    

class MinecraftFormatting:
    """Handles Minecraft text formatting codes"""
    
    FORMATTING_CODES = {
        '§0': ('Black', '#000000'),
        '§1': ('Dark Blue', '#0000AA'),
        '§2': ('Dark Green', '#00AA00'),
        '§3': ('Dark Aqua', '#00AAAA'),
        '§4': ('Dark Red', '#AA0000'),
        '§5': ('Dark Purple', '#AA00AA'),
        '§6': ('Gold', '#FFAA00'),
        '§7': ('Gray', '#AAAAAA'),
        '§8': ('Dark Gray', '#555555'),
        '§9': ('Blue', '#5555FF'),
        '§a': ('Green', '#55FF55'),
        '§b': ('Aqua', '#55FFFF'),
        '§c': ('Red', '#FF5555'),
        '§d': ('Light Purple', '#FF55FF'),
        '§e': ('Yellow', '#FFFF55'),
        '§f': ('White', '#FFFFFF'),
        '§k': ('Obfuscated', None),
        '§l': ('Bold', None),
        '§m': ('Strikethrough', None),
        '§n': ('Underline', None),
        '§o': ('Italic', None),
        '§r': ('Reset', None)
    }
    
    @staticmethod
    def detect_formatting(text: str) -> bool:
        """Check if text contains Minecraft formatting codes"""
        return bool(re.search(r'§[0-9a-fklmnor]', text))
    
    @staticmethod
    def strip_formatting(text: str) -> str:
        """Remove all formatting codes from text"""
        return re.sub(r'§[0-9a-fklmnor]', '', text)
    
    @staticmethod
    def preview_formatting(text: str) -> str:
        """Convert Minecraft formatting to HTML for preview"""
        html = text
        
        # Color codes
        for code, (name, color) in MinecraftFormatting.FORMATTING_CODES.items():
            if color:
                html = html.replace(code, f'<span style="color: {color}">')
            elif code == '§l':
                html = html.replace(code, '<strong>')
            elif code == '§o':
                html = html.replace(code, '<em>')
            elif code == '§n':
                html = html.replace(code, '<u>')
            elif code == '§m':
                html = html.replace(code, '<s>')
            elif code == '§r':
                html = html.replace(code, '</span></strong></em></u></s>')
        
        return html
    
    @staticmethod
    def get_formatted_segments(text: str) -> List[Tuple[str, str, bool, bool, bool, bool]]:
        """Parse text into segments with formatting information
        Returns list of (text, color, bold, italic, underline, strikethrough)"""
        segments = []
        current_text = ""
        current_color = "#ffffff"  # Default white
        current_bold = False
        current_italic = False
        current_underline = False
        current_strikethrough = False
        
        i = 0
        while i < len(text):
            if i < len(text) - 1 and text[i] == '§':
                # Save current segment if we have text
                if current_text:
                    segments.append((current_text, current_color, current_bold, 
                                   current_italic, current_underline, current_strikethrough))
                    current_text = ""
                
                # Process formatting code
                code = text[i:i+2]
                if code in MinecraftFormatting.FORMATTING_CODES:
                    name, color = MinecraftFormatting.FORMATTING_CODES[code]
                    
                    if color:  # Color code
                        current_color = color
                    elif code == '§l':
                        current_bold = True
                    elif code == '§o':
                        current_italic = True
                    elif code == '§n':
                        current_underline = True
                    elif code == '§m':
                        current_strikethrough = True
                    elif code == '§r':
                        # Reset all formatting
                        current_color = "#ffffff"
                        current_bold = False
                        current_italic = False
                        current_underline = False
                        current_strikethrough = False
                
                i += 2
            else:
                current_text += text[i]
                i += 1
        
        # Add final segment
        if current_text:
            segments.append((current_text, current_color, current_bold, 
                           current_italic, current_underline, current_strikethrough))
        
        return segments


class TranslationManager:
    """Main class for managing translations"""
    
    def __init__(self, lang_folder: str):
        self.lang_folder = Path(lang_folder)
        self.translations: Dict[str, Dict[str, TranslationEntry]] = {}
        self.categories: Set[str] = set()
        self.available_languages: Set[str] = set()
        self.base_language = "en_us"
        
    def scan_translations(self) -> None:
        """Scan the lang folder and load all translations"""
        self.translations.clear()
        self.categories.clear()
        self.available_languages.clear()
        
        if not self.lang_folder.exists():
            raise FileNotFoundError(f"Language folder not found: {self.lang_folder}")
        
        # Find all language files
        for category_path in self.lang_folder.iterdir():
            if not category_path.is_dir():
                continue
                
            category = category_path.name
            self.categories.add(category)
            
            for lang_file in category_path.glob("*.json"):
                language = lang_file.stem
                self.available_languages.add(language)
                
                # Load translations from file
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    for key, value in data.items():
                        if language not in self.translations:
                            self.translations[language] = {}
                        
                        # Determine subcategory from key structure
                        subcategory = self._determine_subcategory(key, category)
                        
                        # Get English text if available
                        english_text = ""
                        if language == self.base_language:
                            english_text = value
                        elif self.base_language in self.translations and key in self.translations[self.base_language]:
                            english_text = self.translations[self.base_language][key].english_text
                        
                        entry = TranslationEntry(
                            key=key,
                            category=category,
                            subcategory=subcategory,
                            english_text=english_text if language == self.base_language else "",
                            translated_text=value,
                            has_formatting=MinecraftFormatting.detect_formatting(value)
                        )
                        
                        self.translations[language][key] = entry
                        
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"Error loading {lang_file}: {e}")
        
        # Update English text for all languages
        if self.base_language in self.translations:
            for lang, entries in self.translations.items():
                if lang != self.base_language:
                    for key, entry in entries.items():
                        if key in self.translations[self.base_language]:
                            entry.english_text = self.translations[self.base_language][key].translated_text
    
    def _determine_subcategory(self, key: str, category: str) -> str:
        """Determine subcategory based on key structure"""
        parts = key.split('.')
        if len(parts) >= 2:
            return parts[1]
        return "general"
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        return sorted(self.categories)
    
    def get_subcategories(self, category: str) -> List[str]:
        """Get list of subcategories for a specific category"""
        subcategories = set()
        for lang_entries in self.translations.values():
            for entry in lang_entries.values():
                if entry.category == category:
                    subcategories.add(entry.subcategory)
        return sorted(subcategories)
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        return sorted(self.available_languages)
    
    def get_translations(self, language: str, category: str = None, subcategory: str = None) -> List[TranslationEntry]:
        """Get translations for a specific language with optional filtering"""
        if language not in self.translations:
            return []
        
        entries = []
        for entry in self.translations[language].values():
            if category and entry.category != category:
                continue
            if subcategory and entry.subcategory != subcategory:
                continue
            entries.append(entry)
        
        return sorted(entries, key=lambda x: x.key)
    
    def update_translation(self, language: str, key: str, translated_text: str) -> bool:
        """Update a translation entry"""
        if language == self.base_language:
            return False  # Don't allow editing base language
        
        if language in self.translations and key in self.translations[language]:
            self.translations[language][key].translated_text = translated_text
            self.translations[language][key].has_formatting = MinecraftFormatting.detect_formatting(translated_text)
            return True
        return False
    
    def add_language(self, language_code: str) -> bool:
        """Add a new language with all keys from base language"""
        if language_code in self.available_languages:
            return False
        
        if self.base_language not in self.translations:
            return False
        
        # Create new language with empty translations
        self.translations[language_code] = {}
        for key, base_entry in self.translations[self.base_language].items():
            new_entry = TranslationEntry(
                key=key,
                category=base_entry.category,
                subcategory=base_entry.subcategory,
                english_text=base_entry.translated_text,
                translated_text="",  # Empty for new language
                has_formatting=base_entry.has_formatting
            )
            self.translations[language_code][key] = new_entry
        
        self.available_languages.add(language_code)
        return True
    
    def save_translations(self, language: str = None) -> bool:
        """Save translations to JSON files"""
        languages_to_save = [language] if language else self.available_languages
        
        for lang in languages_to_save:
            if lang not in self.translations:
                continue
            
            # Group translations by category
            categories_data = {}
            for entry in self.translations[lang].values():
                if entry.category not in categories_data:
                    categories_data[entry.category] = {}
                categories_data[entry.category][entry.key] = entry.translated_text
            
            # Save each category to its file
            for category, data in categories_data.items():
                category_dir = self.lang_folder / category
                category_dir.mkdir(exist_ok=True)
                
                file_path = category_dir / f"{lang}.json"
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
                except Exception as e:
                    print(f"Error saving {file_path}: {e}")
                    return False
        
        return True
    
    def search_translations(self, query: str, language: str = None) -> List[TranslationEntry]:
        """Search translations by key or text content"""
        results = []
        languages_to_search = [language] if language else self.available_languages
        
        query_lower = query.lower()
        
        for lang in languages_to_search:
            if lang not in self.translations:
                continue
            
            for entry in self.translations[lang].values():
                if (query_lower in entry.key.lower() or 
                    query_lower in entry.english_text.lower() or 
                    query_lower in entry.translated_text.lower()):
                    results.append(entry)
        
        return results
    
    def get_translation_stats(self, language: str) -> Dict[str, int]:
        """Get translation statistics for a language"""
        if language not in self.translations:
            return {}
        
        total = len(self.translations[language])
        translated = sum(1 for entry in self.translations[language].values() 
                        if entry.translated_text.strip())
        
        return {
            'total': total,
            'translated': translated,
            'untranslated': total - translated,
            'percentage': round((translated / total * 100) if total > 0 else 0, 1)
        }
    
    def validate_translations(self, language: str) -> List[Tuple[str, str]]:
        """Validate translations and return list of issues"""
        issues = []
        
        if language not in self.translations:
            return issues
        
        for entry in self.translations[language].values():
            # Check for empty translations
            if not entry.translated_text.strip():
                issues.append((entry.key, "Empty translation"))
                continue
            
            # Check for placeholder mismatches
            if self.base_language in self.translations:
                base_entry = self.translations[self.base_language].get(entry.key)
                if base_entry:
                    base_placeholders = re.findall(r'%\d+\$[sd]|\{[^}]+\}', base_entry.translated_text)
                    trans_placeholders = re.findall(r'%\d+\$[sd]|\{[^}]+\}', entry.translated_text)
                    
                    if set(base_placeholders) != set(trans_placeholders):
                        issues.append((entry.key, f"Placeholder mismatch: expected {base_placeholders}, got {trans_placeholders}"))
        
        return issues
