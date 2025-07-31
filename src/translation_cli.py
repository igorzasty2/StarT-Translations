"""
Command Line Interface for StarT Translation Manager
"""

import argparse
import sys
from pathlib import Path
from translation_manager import TranslationManager


def list_languages(manager: TranslationManager):
    """List all available languages"""
    languages = manager.get_available_languages()
    print("Available languages:")
    for lang in languages:
        stats = manager.get_translation_stats(lang)
        print(f"  {lang}: {stats['translated']}/{stats['total']} ({stats['percentage']}%)")


def list_categories(manager: TranslationManager):
    """List all categories"""
    categories = manager.get_categories()
    print("Available categories:")
    for cat in categories:
        subcats = manager.get_subcategories(cat)
        print(f"  {cat}: {', '.join(subcats)}")


def add_language(manager: TranslationManager, language_code: str):
    """Add a new language"""
    if manager.add_language(language_code):
        print(f"Successfully added language: {language_code}")
        if manager.save_translations(language_code):
            print(f"Saved translation files for {language_code}")
        else:
            print("Warning: Failed to save translation files")
    else:
        print(f"Failed to add language: {language_code}")


def validate_language(manager: TranslationManager, language_code: str):
    """Validate translations for a language"""
    issues = manager.validate_translations(language_code)
    if issues:
        print(f"Found {len(issues)} validation issues for {language_code}:")
        for key, issue in issues:
            print(f"  {key}: {issue}")
    else:
        print(f"No validation issues found for {language_code}")


def export_untranslated(manager: TranslationManager, language_code: str, output_file: str):
    """Export untranslated keys to a file"""
    translations = manager.get_translations(language_code)
    untranslated = [entry for entry in translations if not entry.translated_text.strip()]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Untranslated keys for {language_code}\n")
        f.write("=" * 50 + "\n\n")
        
        current_category = None
        for entry in sorted(untranslated, key=lambda x: (x.category, x.key)):
            if entry.category != current_category:
                current_category = entry.category
                f.write(f"\n## {current_category}\n\n")
            
            f.write(f"Key: {entry.key}\n")
            f.write(f"English: {entry.english_text}\n")
            f.write(f"Translation: [TODO]\n\n")
    
    print(f"Exported {len(untranslated)} untranslated keys to {output_file}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='StarT Translation Manager CLI')
    parser.add_argument('workspace', help='Path to the language folder')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List commands
    subparsers.add_parser('list-languages', help='List all available languages')
    subparsers.add_parser('list-categories', help='List all categories')
    
    # Language management
    add_lang_parser = subparsers.add_parser('add-language', help='Add a new language')
    add_lang_parser.add_argument('language_code', help='Language code (e.g., fr_fr)')
    
    # Validation
    validate_parser = subparsers.add_parser('validate', help='Validate translations')
    validate_parser.add_argument('language_code', help='Language code to validate')
    
    # Export
    export_parser = subparsers.add_parser('export-untranslated', help='Export untranslated keys')
    export_parser.add_argument('language_code', help='Language code')
    export_parser.add_argument('output_file', help='Output file path')
    
    # Statistics
    stats_parser = subparsers.add_parser('stats', help='Show translation statistics')
    stats_parser.add_argument('language_code', nargs='?', help='Language code (optional)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize translation manager
    try:
        manager = TranslationManager(args.workspace)
        manager.scan_translations()
    except Exception as e:
        print(f"Error loading workspace: {e}")
        sys.exit(1)
    
    # Execute commands
    try:
        if args.command == 'list-languages':
            list_languages(manager)
        
        elif args.command == 'list-categories':
            list_categories(manager)
        
        elif args.command == 'add-language':
            add_language(manager, args.language_code)
        
        elif args.command == 'validate':
            validate_language(manager, args.language_code)
        
        elif args.command == 'export-untranslated':
            export_untranslated(manager, args.language_code, args.output_file)
        
        elif args.command == 'stats':
            if args.language_code:
                stats = manager.get_translation_stats(args.language_code)
                print(f"Statistics for {args.language_code}:")
                print(f"  Total: {stats['total']}")
                print(f"  Translated: {stats['translated']}")
                print(f"  Untranslated: {stats['untranslated']}")
                print(f"  Progress: {stats['percentage']}%")
            else:
                list_languages(manager)
    
    except Exception as e:
        print(f"Error executing command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
