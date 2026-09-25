---
eyebrow: Báo cáo kinh doanh
subtitle: Tổng quan doanh thu, đơn hàng và hiệu suất theo khu vực. (Template mẫu — thay bằng template thật.)
owner: Phòng Kinh doanh
period: { from: "{{ period.from }}", to: "{{ period.to }}" }
compare_label: so với {{ previous_label }}
sources: {{ sources | tojson }}
---

# Báo cáo doanh thu {{ period_label }}

## Chỉ số chính

```kpis
- { label: Doanh thu, value: {{ revenue }}, previous: {{ revenue_prev }}, format: currency, compact: true }
- { label: Số đơn hàng, value: {{ orders }}, previous: {{ orders_prev }}, format: number }
- { label: Tỷ lệ hoàn hàng, value: {{ return_rate }}, previous: {{ return_rate_prev }}, format: percent, invert: true }
```

## Tóm tắt

Trong {{ period_label }}, doanh thu đạt **{{ revenue | currency }}**, {{ "tăng" if revenue >= revenue_prev else "giảm" }}
**{{ ((revenue - revenue_prev) / revenue_prev) | delta }}** {{ compare_label_short }}. Tổng số đơn là
**{{ orders | number }}**, giá trị đơn trung bình **{{ (revenue / orders) | currency }}**.

## Doanh thu theo tuần

```chart
chart: line
format: currency
compact: true
labels: {{ weekly.labels | tojson }}
series:
  - { name: "{{ period_short }}", data: {{ weekly.current | tojson }} }
  - { name: "{{ previous_label }}", data: {{ weekly.previous | tojson }}, dashed: true }
```

## Chi tiết theo khu vực

| Khu vực | Đơn hàng | Doanh thu | Tăng trưởng |
|---|---:|---:|---:|
{% for r in regions -%}
| {{ r.name }} | {{ r.orders | number }} | {{ r.revenue | currency }} | {{ r.growth | delta }} |
{% endfor %}

## Nhận định

{% for item in insights -%}
- {{ item }}
{% endfor %}

> [!warn] Tỷ lệ hoàn hàng Miền Trung ({{ regions[1].return_rate | percent }}) vẫn cao hơn trung bình ({{ return_rate | percent }}).
