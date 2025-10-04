#!/usr/bin/env python3
"""
Script to add reflection document translation keys to i18n-config.json
Adds 8 keys (reflection_title, implementation_summary, etc.) to 11 remaining languages
"""

import json

# Translation data for 11 remaining languages (en, ru, uk already done)
TRANSLATIONS = {
    "de": {
        "reflection_title": "Reflexion",
        "implementation_summary": "Implementierungszusammenfassung",
        "what_went_well": "Was gut lief",
        "challenges_encountered": "Aufgetretene Herausforderungen",
        "lessons_learned": "Gelernte Lektionen",
        "improvements_future": "Verbesserungen für die Zukunft",
        "plan_vs_reality": "Plan vs Realität",
        "actionable_next_steps": "Umsetzbare nächste Schritte",
        "key_takeaways": "Wichtige Erkenntnisse"
    },
    "fr": {
        "reflection_title": "Réflexion",
        "implementation_summary": "Résumé de l'implémentation",
        "what_went_well": "Ce qui s'est bien passé",
        "challenges_encountered": "Défis rencontrés",
        "lessons_learned": "Leçons apprises",
        "improvements_future": "Améliorations pour l'avenir",
        "plan_vs_reality": "Plan vs Réalité",
        "actionable_next_steps": "Prochaines étapes concrètes",
        "key_takeaways": "Points clés à retenir"
    },
    "es": {
        "reflection_title": "Reflexión",
        "implementation_summary": "Resumen de implementación",
        "what_went_well": "Lo que salió bien",
        "challenges_encountered": "Desafíos encontrados",
        "lessons_learned": "Lecciones aprendidas",
        "improvements_future": "Mejoras para el futuro",
        "plan_vs_reality": "Plan vs Realidad",
        "actionable_next_steps": "Próximos pasos accionables",
        "key_takeaways": "Conclusiones clave"
    },
    "pt": {
        "reflection_title": "Reflexão",
        "implementation_summary": "Resumo da implementação",
        "what_went_well": "O que correu bem",
        "challenges_encountered": "Desafios encontrados",
        "lessons_learned": "Lições aprendidas",
        "improvements_future": "Melhorias para o futuro",
        "plan_vs_reality": "Plano vs Realidade",
        "actionable_next_steps": "Próximos passos acionáveis",
        "key_takeaways": "Principais conclusões"
    },
    "it": {
        "reflection_title": "Riflessione",
        "implementation_summary": "Riepilogo implementazione",
        "what_went_well": "Cosa è andato bene",
        "challenges_encountered": "Sfide incontrate",
        "lessons_learned": "Lezioni apprese",
        "improvements_future": "Miglioramenti futuri",
        "plan_vs_reality": "Piano vs Realtà",
        "actionable_next_steps": "Prossimi passi attuabili",
        "key_takeaways": "Punti chiave"
    },
    "ja": {
        "reflection_title": "リフレクション",
        "implementation_summary": "実装の概要",
        "what_went_well": "うまくいったこと",
        "challenges_encountered": "遭遇した課題",
        "lessons_learned": "学んだ教訓",
        "improvements_future": "将来の改善",
        "plan_vs_reality": "計画 vs 現実",
        "actionable_next_steps": "実行可能な次のステップ",
        "key_takeaways": "重要なポイント"
    },
    "zh": {
        "reflection_title": "反思",
        "implementation_summary": "实施摘要",
        "what_went_well": "进展顺利的事项",
        "challenges_encountered": "遇到的挑战",
        "lessons_learned": "汲取的教训",
        "improvements_future": "未来改进",
        "plan_vs_reality": "计划 vs 现实",
        "actionable_next_steps": "可执行的后续步骤",
        "key_takeaways": "关键要点"
    },
    "ko": {
        "reflection_title": "회고",
        "implementation_summary": "구현 요약",
        "what_went_well": "잘된 점",
        "challenges_encountered": "직면한 과제",
        "lessons_learned": "배운 교훈",
        "improvements_future": "향후 개선 사항",
        "plan_vs_reality": "계획 vs 현실",
        "actionable_next_steps": "실행 가능한 다음 단계",
        "key_takeaways": "핵심 사항"
    },
    "ar": {
        "reflection_title": "التأمل",
        "implementation_summary": "ملخص التنفيذ",
        "what_went_well": "ما سار بشكل جيد",
        "challenges_encountered": "التحديات التي واجهتها",
        "lessons_learned": "الدروس المستفادة",
        "improvements_future": "التحسينات المستقبلية",
        "plan_vs_reality": "الخطة مقابل الواقع",
        "actionable_next_steps": "الخطوات التالية القابلة للتنفيذ",
        "key_takeaways": "النقاط الرئيسية"
    },
    "hi": {
        "reflection_title": "चिंतन",
        "implementation_summary": "कार्यान्वयन सारांश",
        "what_went_well": "क्या अच्छा रहा",
        "challenges_encountered": "आई हुई चुनौतियाँ",
        "lessons_learned": "सीखे गए सबक",
        "improvements_future": "भविष्य के सुधार",
        "plan_vs_reality": "योजना बनाम वास्तविकता",
        "actionable_next_steps": "कार्यान्वयन योग्य अगले कदम",
        "key_takeaways": "मुख्य बातें"
    },
    "pl": {
        "reflection_title": "Refleksja",
        "implementation_summary": "Podsumowanie implementacji",
        "what_went_well": "Co poszło dobrze",
        "challenges_encountered": "Napotkane wyzwania",
        "lessons_learned": "Wyciągnięte wnioski",
        "improvements_future": "Ulepszenia na przyszłość",
        "plan_vs_reality": "Plan vs Rzeczywistość",
        "actionable_next_steps": "Możliwe do wdrożenia kolejne kroki",
        "key_takeaways": "Kluczowe wnioski"
    },
    "tr": {
        "reflection_title": "Yansıma",
        "implementation_summary": "Uygulama Özeti",
        "what_went_well": "İyi Giden Şeyler",
        "challenges_encountered": "Karşılaşılan Zorluklar",
        "lessons_learned": "Öğrenilen Dersler",
        "improvements_future": "Gelecek İçin İyileştirmeler",
        "plan_vs_reality": "Plan vs Gerçeklik",
        "actionable_next_steps": "Uygulanabilir Sonraki Adımlar",
        "key_takeaways": "Ana Çıkarımlar"
    }
}

def main():
    config_path = "e:/My/vscode-memory-bank/.vscode/memory-bank/i18n-config.json"
    
    # Read current config
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Add translations to each language
    updated_count = 0
    for lang_code, translations in TRANSLATIONS.items():
        if lang_code in config["messages"]:
            for key, value in translations.items():
                config["messages"][lang_code][key] = value
            updated_count += 1
            print(f"✅ Added 9 keys to '{lang_code}'")
        else:
            print(f"⚠️  Language '{lang_code}' not found in config")
    
    # Save updated config
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Updated {updated_count} languages in i18n-config.json")
    print(f"Total reflection keys per language: 9")
    print(f"Languages updated: {', '.join(TRANSLATIONS.keys())}")

if __name__ == "__main__":
    main()
