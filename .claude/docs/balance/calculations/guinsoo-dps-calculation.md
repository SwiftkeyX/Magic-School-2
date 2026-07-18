# Guinsoo's Rageblade AS Ramp Calculations — Tristana 💣

This document provides a detailed mathematical breakdown of how **Guinsoo's Rageblade** ramps Attack Speed (AS) for Tristana over 15-second and 30-second combat durations using the simplified **Time-Based Ramp Model**.

---

## ⚙️ Core Variables & Mechanics

The calculations are driven by the following parameters:

*   **Base Attack Speed ($AS_{\text{base}}$):** $0.70$
*   **Equipped Flat AS Bonus:** $+28\%$ total
    *   *Guinsoo's Rageblade base:* $+18\%$
    *   *Last Whisper base:* $+10\%$
*   **Starting Attack Speed ($AS_0$):** $0.70 \times (1.00 + 0.28) = \mathbf{0.896\text{ AS}}$
*   **Guinsoo's Stacking Rate (Time-Based):** 
    *   **Rate:** 1 stack per second ($S(t) = t$)
    *   **Value per Stack:** $+7\%$ of base AS ($+0.049\text{ AS}$ per stack)
*   **Tristana Spell Steroid:** $+1.00$ flat AS (applied only during active buff phases)
*   **Attacks to Cast (ATC):** $4$ attacks (charges 40 max mana, followed by a 4.0s steroid with mana lock)

---

## 📊 Mathematical Modeling of Averages

Because Guinsoo stacks increase linearly with time ($S(t) = t$), the equipped non-steroid AS at any second $t$ is:
$$AS(t) = AS_0 + t \times 0.049 = 0.896 + t \times 0.049$$

The average equipped AS over a fight of duration $T$ is the value at the midpoint of the fight ($t = T / 2$):
$$AS_{\text{equipped\_avg}} = AS_0 + \frac{T}{2} \times 0.049$$

The average steroid AS during the buff phases is simply:
$$AS_{\text{steroid\_avg}} = AS_{\text{equipped\_avg}} + 1.00$$

---

## 🧮 15-Second Combat Calculations ($T = 15\text{s}$)

1.  **Average Equipped AS ($AS_{\text{equipped}}$):**
    $$AS_{\text{equipped}} = 0.896 + 7.5 \times 0.049 = \mathbf{1.26\text{ AS}} \text{ (rounded from 1.2635)}$$
2.  **Average Steroid AS ($AS_{\text{steroid}}$):**
    $$AS_{\text{steroid}} = 1.26 + 1.00 = \mathbf{2.26\text{ AS}}$$
3.  **Cycle Duration:**
    $$\text{Cycle Duration} = \frac{4}{1.26} + 4.0 = 3.175\text{s} + 4.0\text{s} = \mathbf{7.175\text{s}}$$
4.  **Attacks per Cycle:**
    *   *Mana Gen Attacks:* $4$
    *   *Steroid Attacks:* $4.0\text{s} \times 2.26\text{ AS} = 9.04$ attacks
    *   *Total Attacks:* $4 + 9.04 = \mathbf{13.04\text{ attacks}}$

---

## 🧮 30-Second Combat Calculations ($T = 30\text{s}$)

1.  **Average Equipped AS ($AS_{\text{equipped}}$):**
    $$AS_{\text{equipped}} = 0.896 + 15.0 \times 0.049 = \mathbf{1.63\text{ AS}} \text{ (rounded from 1.631)}$$
2.  **Average Steroid AS ($AS_{\text{steroid}}$):**
    $$AS_{\text{steroid}} = 1.63 + 1.00 = \mathbf{2.63\text{ AS}}$$
3.  **Cycle Duration:**
    $$\text{Cycle Duration} = \frac{4}{1.63} + 4.0 = 2.454\text{s} + 4.0\text{s} = \mathbf{6.454\text{s}}$$
4.  **Attacks per Cycle:**
    *   *Mana Gen Attacks:* $4$
    *   *Steroid Attacks:* $4.0\text{s} \times 2.63\text{ AS} = 10.52$ attacks
    *   *Total Attacks:* $4 + 10.52 = \mathbf{14.52\text{ attacks}}$

---

## 🔍 Model Summary Table

| Fight Duration ($T$) | Midpoint ($T/2$) | Average Stacks | Average Equipped AS | Average Steroid AS | Cycle Duration | Total Cycle Attacks |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **15 Seconds** | $7.5\text{s}$ | $7.5$ | **1.26** | **2.26** | **7.175s** | **13.04** |
| **30 Seconds** | $15.0\text{s}$ | $15.0$ | **1.63** | **2.63** | **6.454s** | **14.52** |
