# 3D Pallet Stacker

Sistema completo para calcular e visualizar empilhamento de caixas em pallets usando grade de 1" cúbico.

## 📁 Arquivos do Projeto

### Arquivos Principais
- **`pallet_3d.html`** - Interface web com visualizador 3D
- **`pallet_calculator.py`** - Servidor Python com algoritmo de cálculo
- **`START_PALLET_STACKER.bat`** - Script para iniciar o servidor

### Documentação
- **`README.md`** - Este arquivo (guia principal)
- **`README_NEW.md`** - Documentação detalhada em inglês
- **`TROUBLESHOOTING.md`** - Guia de solução de problemas

## 🚀 Como Usar

1. **Inicie o servidor**: Duplo-clique em `START_PALLET_STACKER.bat`
2. **Abra no navegador**: `http://localhost:8000/pallet_3d.html`
3. **Adicione caixas**: Preencha nome, dimensões, peso, quantidade e cor
4. **Calcule**: Clique em "Calculate Pallets"
5. **Visualize**: Veja os pallets em 3D e siga os passos

## 📋 Especificações

- **Base do pallet**: 40" × 48" polegadas
- **Altura máxima**: 65 polegadas (incluindo base de 6")
- **Peso máximo**: 1400 libras por pallet
- **Sistema**: Grade de 1" × 1" × 1" cubos

## ⚙️ Requisitos

- Python 3.6 ou superior
- Navegador moderno com suporte WebGL (Chrome, Firefox, Edge)
- Conexão com internet (para carregar Three.js)

## 🆘 Problemas?

Consulte `TROUBLESHOOTING.md` para soluções de problemas comuns.

