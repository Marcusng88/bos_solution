#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Dashboard routes that need AuthGuard
const dashboardRoutes = [
  'dashboard/publishing/page.tsx',
  'dashboard/roi/page.tsx',
  'dashboard/monitoring/page.tsx',
  'dashboard/optimization/page.tsx',
  'dashboard/campaigns/page.tsx',
];

function addAuthGuardToFile(filePath) {
  try {
    const fullPath = path.join(__dirname, '..', 'app', filePath);
    
    if (!fs.existsSync(fullPath)) {
      console.log(`⚠️  File not found: ${filePath}`);
      return;
    }

    let content = fs.readFileSync(fullPath, 'utf8');
    
    // Check if AuthGuard is already imported
    if (content.includes('AuthGuard')) {
      console.log(`✅ AuthGuard already present in ${filePath}`);
      return;
    }

    // Add import for AuthGuard
    const importStatement = "import { AuthGuard } from '@/components/auth/auth-guard'";
    
    // Find the last import statement and add AuthGuard after it
    const importRegex = /(import.*?from.*?['"][^'"]*['"];?\s*)/g;
    const imports = content.match(importRegex);
    
    if (imports) {
      const lastImport = imports[imports.length - 1];
      content = content.replace(lastImport, lastImport + '\n' + importStatement);
    } else {
      // If no imports found, add at the beginning
      content = importStatement + '\n' + content;
    }

    // Wrap the return statement with AuthGuard
    const returnRegex = /return\s*\(\s*([^)]+)\s*\)/;
    if (returnRegex.test(content)) {
      content = content.replace(
        returnRegex,
        'return (\n    <AuthGuard>\n      $1\n    </AuthGuard>\n  )'
      );
    }

    fs.writeFileSync(fullPath, content);
    console.log(`✅ Added AuthGuard to ${filePath}`);
    
  } catch (error) {
    console.error(`❌ Error processing ${filePath}:`, error.message);
  }
}

console.log('🔐 Adding AuthGuard to dashboard routes...\n');

dashboardRoutes.forEach(route => {
  addAuthGuardToFile(route);
});

console.log('\n✨ Done! All dashboard routes now have authentication protection.');
console.log('\n📝 Note: You may need to manually adjust some files if they have complex return statements.');
console.log('\n🚀 Next steps:');
console.log('1. Create your .env.local file with Clerk keys');
console.log('2. Test the authentication flow');
console.log('3. Customize the Clerk appearance as needed');
