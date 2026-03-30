# Arquitetura técnica (MVP)

## Pipeline

1. **EEG Input**
   - Recebe stream de métricas (bandas ou observáveis do SDK).
2. **Calibration Engine**
   - Coleta dados de baseline em blocos temporais e gera *Adaptive Thresholds*.
3. **HyperBitnet**
   - Componente lógico que transforma ou eleva os sinais em vetores num formato quântico simulado.
4. **Fusion & TRIBE**
   - Funil que agrega o output e adapta para o dialeto do sistema final via `tribe_adapter`.
