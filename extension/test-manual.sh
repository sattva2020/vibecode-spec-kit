#!/bin/bash
# Phase 1 Manual Testing Checklist
# Run this script to get step-by-step testing instructions

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  VS Code Memory Bank Extension - Phase 1 Testing          ║"
echo "║  Date: $(date +%Y-%m-%d)                                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 Prerequisites Check:"
echo "  ✓ Extension compiled (dist/extension.js exists)"
echo "  ✓ Size: $(ls -lh dist/extension.js | awk '{print $5}')"
echo ""

echo "🚀 STEP 1: Launch Extension Development Host"
echo "────────────────────────────────────────────────────────────"
echo "  1. Ensure you're in the extension workspace"
echo "  2. Press F5 (or Run → Start Debugging)"
echo "  3. Wait for 'Extension Development Host' window to open"
echo "  4. Check Debug Console for: 'Memory Bank extension activating...'"
echo ""
echo "  Expected: Extension loads without errors"
echo ""
read -p "Press Enter when Extension Development Host is running..."
echo ""

echo "✅ TEST 1: Extension Activation"
echo "────────────────────────────────────────────────────────────"
echo "  Check Debug Console (Extension Host) for messages:"
echo "  • 'Memory Bank extension activating...'"
echo "  • 'Memory Bank not detected: ...' OR 'Memory Bank detected at: ...'"
echo "  • 'Memory Bank extension activated successfully'"
echo ""
echo "  Check Status Bar (bottom left):"
echo "  • Should show: ⚠️ Memory Bank (if not initialized)"
echo "  • OR: 🗄️ Memory Bank (if already initialized)"
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test1
echo ""

echo "✅ TEST 2: Command Palette Integration"
echo "────────────────────────────────────────────────────────────"
echo "  In Extension Development Host:"
echo "  1. Press Ctrl+Shift+P (Command Palette)"
echo "  2. Type 'Memory Bank'"
echo "  3. Verify ALL 9 commands appear:"
echo "     • Memory Bank: VAN Mode"
echo "     • Memory Bank: PLAN Mode"
echo "     • Memory Bank: CREATIVE Mode"
echo "     • Memory Bank: IMPLEMENT Mode"
echo "     • Memory Bank: REFLECT Mode"
echo "     • Memory Bank: ARCHIVE Mode"
echo "     • Memory Bank: SYNC Mode"
echo "     • Memory Bank: Setup Wizard"
echo "     • Memory Bank: Show Status"
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test2
echo ""

echo "✅ TEST 3: Setup Wizard"
echo "────────────────────────────────────────────────────────────"
echo "  1. Open an EMPTY folder in Extension Development Host"
echo "  2. Command Palette → 'Memory Bank: Setup Wizard'"
echo "  3. Wait for progress notification"
echo "  4. Check for success message: '✅ Memory Bank initialized successfully!'"
echo "  5. Verify files created:"
echo "     • .vscode/memory-bank/tasks.md"
echo "     • .vscode/memory-bank/activeContext.md"
echo "     • .vscode/memory-bank/progress.md"
echo "     • .vscode/memory-bank/projectbrief.md"
echo "     • .vscode/memory-bank/.language"
echo "     • .vscode/memory-bank/creative/"
echo "     • .vscode/memory-bank/reflection/"
echo "     • .vscode/memory-bank/archive/"
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test3
echo ""

echo "✅ TEST 4: Settings UI"
echo "────────────────────────────────────────────────────────────"
echo "  1. File → Preferences → Settings (Ctrl+,)"
echo "  2. Search: 'Memory Bank'"
echo "  3. Verify 4 settings visible:"
echo "     • Language (dropdown, 15 options: en, ru, uk, de, fr...)"
echo "     • Default Complexity (dropdown, 4 levels)"
echo "     • Auto Save (checkbox, enabled by default)"
echo "     • Templates Path (text field, empty by default)"
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test4
echo ""

echo "✅ TEST 5: Show Status Command"
echo "────────────────────────────────────────────────────────────"
echo "  1. Command Palette → 'Memory Bank: Show Status'"
echo "  2. Output Channel should open: 'Memory Bank Status'"
echo "  3. Verify content:"
echo "     • ✅ Memory Bank: ACTIVE"
echo "     • 📁 Location: [path]"
echo "     • Configuration: Language, Complexity, Auto-Save, Templates"
echo "     • Available Modes: VAN, PLAN, CREATIVE, etc."
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test5
echo ""

echo "✅ TEST 6: VAN Mode Command"
echo "────────────────────────────────────────────────────────────"
echo "  1. Command Palette → 'Memory Bank: VAN Mode'"
echo "  2. Expected:"
echo "     • Copilot Chat panel opens"
echo "     • Notification: '💡 Memory Bank: Type \"VAN\" in Copilot Chat...'"
echo "     • Button: 'Got it'"
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test6
echo ""

echo "✅ TEST 7: All Mode Commands (Quick Test)"
echo "────────────────────────────────────────────────────────────"
echo "  Test each command opens Chat + shows notification:"
echo "  • PLAN Mode"
echo "  • CREATIVE Mode"
echo "  • IMPLEMENT Mode"
echo "  • REFLECT Mode"
echo "  • ARCHIVE Mode"
echo "  • SYNC Mode"
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test7
echo ""

echo "✅ TEST 8: Memory Bank Detection Guard"
echo "────────────────────────────────────────────────────────────"
echo "  1. Delete .vscode/memory-bank/ directory"
echo "  2. Reload Extension Development Host (Ctrl+R)"
echo "  3. Run 'Memory Bank: VAN Mode'"
echo "  4. Expected:"
echo "     • Warning: 'Memory Bank not detected...'"
echo "     • Button: 'Setup Wizard'"
echo "     • Chat does NOT open"
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test8
echo ""

echo "✅ TEST 9: Language Detection"
echo "────────────────────────────────────────────────────────────"
echo "  1. Run Setup Wizard again"
echo "  2. Check .vscode/memory-bank/.language file"
echo "  3. Expected: Contains system language code (e.g., 'en', 'ru')"
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test9
echo ""

echo "✅ TEST 10: Status Bar Integration"
echo "────────────────────────────────────────────────────────────"
echo "  1. With Memory Bank initialized: Status bar shows 🗄️ Memory Bank"
echo "  2. Without Memory Bank: Status bar shows ⚠️ Memory Bank"
echo "  3. Click status bar → Opens Status Output (with MB) or Setup (without)"
echo ""
read -p "✓ PASS / ✗ FAIL? (p/f): " test10
echo ""

# Calculate results
tests_passed=0
tests_failed=0

[[ "$test1" == "p" ]] && ((tests_passed++)) || ((tests_failed++))
[[ "$test2" == "p" ]] && ((tests_passed++)) || ((tests_failed++))
[[ "$test3" == "p" ]] && ((tests_passed++)) || ((tests_failed++))
[[ "$test4" == "p" ]] && ((tests_passed++)) || ((tests_failed++))
[[ "$test5" == "p" ]] && ((tests_passed++)) || ((tests_failed++))
[[ "$test6" == "p" ]] && ((tests_passed++)) || ((tests_failed++))
[[ "$test7" == "p" ]] && ((tests_passed++)) || ((tests_failed++))
[[ "$test8" == "p" ]] && ((tests_passed++)) || ((tests_failed++))
[[ "$test9" == "p" ]] && ((tests_passed++)) || ((tests_failed++))
[[ "$test10" == "p" ]] && ((tests_passed++)) || ((tests_failed++))

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Test Results Summary                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "  ✓ Tests Passed: $tests_passed / 10"
echo "  ✗ Tests Failed: $tests_failed / 10"
echo ""

if [ $tests_failed -eq 0 ]; then
    echo "  🎉 ALL TESTS PASSED! Phase 1 complete."
    echo ""
    echo "  Next steps:"
    echo "  1. Document results in progress.md"
    echo "  2. Update tasks.md with Phase 1 completion"
    echo "  3. Consider Phase 2 or REFLECT mode"
else
    echo "  ⚠️ Some tests failed. Review and fix issues."
    echo ""
    echo "  Failed tests:"
    [[ "$test1" == "f" ]] && echo "    • TEST 1: Extension Activation"
    [[ "$test2" == "f" ]] && echo "    • TEST 2: Command Palette Integration"
    [[ "$test3" == "f" ]] && echo "    • TEST 3: Setup Wizard"
    [[ "$test4" == "f" ]] && echo "    • TEST 4: Settings UI"
    [[ "$test5" == "f" ]] && echo "    • TEST 5: Show Status Command"
    [[ "$test6" == "f" ]] && echo "    • TEST 6: VAN Mode Command"
    [[ "$test7" == "f" ]] && echo "    • TEST 7: All Mode Commands"
    [[ "$test8" == "f" ]] && echo "    • TEST 8: Memory Bank Detection Guard"
    [[ "$test9" == "f" ]] && echo "    • TEST 9: Language Detection"
    [[ "$test10" == "f" ]] && echo "    • TEST 10: Status Bar Integration"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
