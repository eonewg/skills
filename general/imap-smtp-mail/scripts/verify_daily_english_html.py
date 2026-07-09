#!/usr/bin/env python3
import json, re, sys
p=sys.argv[1]
data=json.load(open(p,encoding='utf-8'))
html=(data.get('draft') or {}).get('html') or ''
text=(data.get('draft') or {}).get('text') or ''
checks={
 'approvalRequired': data.get('approvalRequired') is True,
 'has_style_tag': '<style>' in html,
 'has_colors_or_backgrounds': ('color:' in html and 'background:' in html),
 'has_responsive_css': '@media (max-width:600px)' in html,
 'has_wide_layout_classes': 'class="section"' in html and 'class="hero"' in html,
 'has_teach_warm_palette': all(x in html.lower() for x in ('#faf9f5', '#cc785c')) and any(x in html.lower() for x in ('#141413', '#3d3d3a')),
 'avoids_high_saturation_old_palette': not any(x in html.lower() for x in ('#2563eb', '#16a34a', '#7c3aed', '#dc2626')),
 'looks_generated_from_text': html.strip().startswith('<p>') and '<style>' not in html,
 'max_width_760_820': bool(re.search(r'max-width\s*:\s*(7[6-9]\d|8[01]\d|820)px', html)),
 'no_nested_section': not bool(re.search(r'<section[^>]*>.*<section', html, re.S)),
 'no_table_layout_for_connectors_replacements': 'class="data-table"' not in html and 'class="table-wrap"' not in html,
 'no_horizontal_row_borders': not bool(re.search(r'border-bottom\s*:', html, re.I)) and '<hr' not in html.lower(),
 'html_len': len(html),
 'text_len': len(text),
}
print(json.dumps(checks,ensure_ascii=False,indent=2))
fail=[k for k,v in checks.items() if (k not in ('looks_generated_from_text','html_len','text_len') and not v) or (k=='looks_generated_from_text' and v)]
if fail:
 print('FAILED: '+', '.join(fail), file=sys.stderr)
 sys.exit(1)
