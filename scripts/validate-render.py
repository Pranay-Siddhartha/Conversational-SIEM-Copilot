#!/usr/bin/env python3
"""
Render Deployment Configuration Validator
Ensures the application is ready for Render deployment
"""

import os
import sys
import json
from pathlib import Path

class RenderValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.root = Path(__file__).parent

    def check_render_yaml(self):
        """Validate render.yaml exists and is valid"""
        render_yaml = self.root / "render.yaml"
        if not render_yaml.exists():
            self.errors.append("❌ render.yaml not found")
            return False
        
        try:
            import yaml
            with open(render_yaml) as f:
                config = yaml.safe_load(f)
            if not config:
                self.errors.append("❌ render.yaml is empty or invalid")
                return False
            print("✅ render.yaml is valid")
            return True
        except ImportError:
            self.warnings.append("⚠️  PyYAML not installed (validation skipped)")
            print("✅ render.yaml exists")
            return True
        except Exception as e:
            self.errors.append(f"❌ render.yaml validation failed: {e}")
            return False

    def check_backend_config(self):
        """Validate backend configuration"""
        issues = []
        
        # Check requirements.txt
        if not (self.root / "backend" / "requirements.txt").exists():
            issues.append("❌ backend/requirements.txt missing")
        else:
            print("✅ backend/requirements.txt found")
        
        # Check main.py
        if not (self.root / "backend" / "main.py").exists():
            issues.append("❌ backend/main.py missing")
        else:
            print("✅ backend/main.py found")
        
        # Check config
        if not (self.root / "backend" / "config.py").exists():
            issues.append("❌ backend/config.py missing")
        else:
            print("✅ backend/config.py found")
        
        return issues

    def check_frontend_config(self):
        """Validate frontend configuration"""
        issues = []
        
        # Check package.json
        if not (self.root / "package.json").exists():
            issues.append("❌ package.json missing")
        else:
            print("✅ package.json found")
        
        # Check Next.js config
        has_next_config = (self.root / "next.config.ts").exists() or (self.root / "next.config.js").exists()
        if not has_next_config:
            issues.append("❌ Neither next.config.ts nor next.config.js found")
        else:
            print("✅ Next.js config found")
        
        # Check src/app
        if not (self.root / "src" / "app").exists():
            issues.append("❌ src/app directory missing")
        else:
            print("✅ src/app directory found")
        
        return issues

    def check_environment_templates(self):
        """Validate environment variable templates"""
        issues = []
        
        if not (self.root / ".env.render.example").exists():
            issues.append("⚠️  .env.render.example missing (helpful but not required)")
        else:
            print("✅ .env.render.example found")
        
        return issues

    def check_database_setup(self):
        """Validate database configuration"""
        issues = []
        
        if not (self.root / "backend" / "db" / "database.py").exists():
            issues.append("❌ backend/db/database.py missing")
        else:
            print("✅ backend/db/database.py found")
        
        return issues

    def check_documentation(self):
        """Validate deployment documentation"""
        docs = {
            "RENDER_DEPLOYMENT.md": "Deployment guide (required)",
            "RENDER_QUICKSTART.md": "Quick start guide (helpful)",
            "MIGRATION_CHECKLIST.md": "Migration checklist (helpful)",
        }
        
        for doc, desc in docs.items():
            if (self.root / doc).exists():
                print(f"✅ {doc} found")
            else:
                self.warnings.append(f"⚠️  {doc} missing ({desc})")

    def validate(self):
        """Run all validations"""
        print("=" * 60)
        print("🔍 Render Deployment Configuration Validator")
        print("=" * 60)
        print()
        
        print("📋 Checking render.yaml...")
        self.check_render_yaml()
        print()
        
        print("🔧 Checking backend configuration...")
        self.errors.extend(self.check_backend_config())
        print()
        
        print("🎨 Checking frontend configuration...")
        self.errors.extend(self.check_frontend_config())
        print()
        
        print("🌍 Checking environment templates...")
        self.warnings.extend(self.check_environment_templates())
        print()
        
        print("💾 Checking database setup...")
        self.errors.extend(self.check_database_setup())
        print()
        
        print("📚 Checking documentation...")
        self.check_documentation()
        print()
        
        # Print summary
        print("=" * 60)
        print("📊 Validation Summary")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
        else:
            print("\n✅ No errors found")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        else:
            print("✅ No warnings")
        
        print()
        
        if self.errors:
            print("❌ Application is NOT ready for Render deployment")
            return False
        else:
            print("✅ Application is ready for Render deployment!")
            print()
            print("📝 Next steps:")
            print("   1. Push changes to GitHub")
            print("   2. Go to https://dashboard.render.com")
            print("   3. Click 'New +' → 'Blueprint'")
            print("   4. Select your repository")
            print("   5. Watch Render deploy automatically")
            return True

if __name__ == "__main__":
    validator = RenderValidator()
    success = validator.validate()
    sys.exit(0 if success else 1)
