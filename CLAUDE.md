# Fashion pose-to-video

Catálogo de vídeos curtos de moda com transferência de movimento no ComfyUI.
Pasta do projeto: `E:\dev\Fashion-pose-to-video` (substitui a antiga `E:\dev\Image Studio\motion`).

## Estrutura da pasta
- `1 - AI instructions\` — briefings e instruções para IA.
- `2 - files\workflows\` — cópias API-JSON dos workflows (W1_api.json, W2_api.json...).
- `3 - Assets\referencias de pose\` — vídeos de referência de movimento (originais).
  Para usar no ComfyUI, copiar para `D:\Comfy-Desktop\ComfyUI-Shared\input\motion\`.

## Objetivo
Extrair o movimento (pose) de vídeos de referência e aplicar numa foto de modelo vestindo uma peça de e-commerce, gerando vídeos curtos. Fase 1 é 100% local (sem gastar crédito). Seedream/API só numa fase futura.

## Regras de trabalho
- NUNCA executar workflows (nada de POST /prompt nem "Run"). Claude monta e salva; o usuário roda manualmente e conta o resultado.
- Usar nós NATIVOS do ComfyUI (não instalar custom nodes) e partir dos templates oficiais instalados.
- Resolução barata (480p) nos testes; qualidade alta só depois de aprovação.
- Downloads de modelos só com autorização.
- **Versionar, não sobrescrever:** mudança em workflow existente = novo arquivo `_v2`, `_v3`… (no ComfyUI, na cópia API e no `build_*.py`).
- **Registrar toda alteração em `HISTORICO.md`** (o quê, onde, antes → depois, por quê), entrada nova no topo.
- Vídeo/imagem pedido pelo usuário vai também no chat (SendUserFile).
- **Toda comparação (versão A × B, antes × depois) vira VÍDEO LADO A LADO simultâneo com rótulos** (`W4_compara_versoes.py` / `W4_lado_a_lado.py`), + zoom lado a lado quando o detalhe importa. Só depois que o ComfyUI estiver livre (nada pesado durante render).

## Repositório
- GitHub **público** (desde 2026-11-22, a pedido do usuário): https://github.com/LuanVelo/fashion-pose-to-video (branch `main`). `README.md` é a documentação pública do projeto: manter atualizado (workflows, modelos, exemplos em `docs/media/`).
- Nunca versionar modelos nem vídeos de `3 - Assets/` (ver `.gitignore`). Após cada entrada no HISTORICO: commit + push.

## Ambiente
- GPU RTX 4090 24 GB, Windows.
- ComfyUI Desktop, instância **cfui01**: `D:\Comfy-Desktop\ComfyUI-Installs\cfui01` — versão 0.46.2, em http://127.0.0.1:8188. Zero custom nodes.
- Python do venv: `D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI\.venv\Scripts\python.exe` (usar com `-I -X utf8`).
- Modelos compartilhados: `D:\Comfy-Desktop\ComfyUI-Shared\models` (também usado pelo portable em `E:\dev\ComfyUI_windows_portable`).
- Input/Output: `D:\Comfy-Desktop\ComfyUI-Shared\input` e `\output`, subpastas `input\motion\` e `output\motion\`.
- Workflows de UI salvos em: `D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI\user\default\workflows\` (prefixo `motion_`).
  **No ComfyUI ficam SÓ os workflows de produção.** Workflows de teste/versões antigas vão para `2 - files\workflows\ui_testes\` (e saem do ComfyUI); cópia dos de produção em `2 - files\workflows\ui_producao\`.
- Templates oficiais: `...\cfui01\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates\`
- Gerar JSON de UI sem executar: carregar o API-JSON no front (browser em 127.0.0.1:8188, `app.loadApiJson`), organizar e salvar via `api.storeUserData('workflows/<nome>.json')`.

## Modelos disponíveis
- MiniMax H3 completo (ref2va, fl2va, LoRAs turbo 4/8 passos, qwen3vl_32b text encoder, VAEs vídeo/áudio) — também usado nos workflows h3_* e vovo_*.
- Flux 2 Klein 9B base + qwen_3_8b (edição/variação de imagem).
- Baixados para este projeto: sdpose_wholebody_fp16 (checkpoints), rt_detr_v4-x-hgnet_fp16 (diffusion_models), minimax_h3_fun_controlnet_union_pruned_int8_convrot (model_patches).
- Plano B NÃO baixado: Wan Animate 2 (~26 GB, template video_wan_animate2) e Qwen Image Edit 2511 (~31 GB).

## Fluxo de produção (3 workflows no ComfyUI, desde 2026-11-22, HISTORICO #33)
1. **`motion_W1_extrai-pose_v2`** (PRODUÇÃO 1/3, `build_W1_v2.py`): vídeo de referência + nome da pose + trecho em segundos (início, duração 5,2 s) → recorte pelo fps (ComfyMathExpression) → 124 quadros → SDPose sem rosto, com cabeça → `output/motion/catalogo/<pose>/` (pose_*.mp4, original_*.mp4, keyframes). Depois: `catalogo.py pose <pose>` copia para `input/motion/poses/<pose>/pose.mp4` + `original.mp4`.
2. **`motion_W5_qualidade_v10`** (PRODUÇÃO 2/3, `build_W5_v10.py`): = W5 v9 lendo `motion/poses/<pose>/pose.mp4`; pose do primeiro quadro = quadro 0 do pose.mp4 (ImageFromBatch). Saída `output/motion/producao/<produto>_<pose>/` (frame0, video). Depois: `catalogo.py comparativo <nome> <pose>` e `catalogo.py upscale <nome>`.
3. **`motion_W6_upscale_v2`** (PRODUÇÃO 3/3, `build_W6_v2.py`): RelayVSR x2 de `input/motion/producao/<nome>.mp4` → mesma pasta de produção (video_2x 1792×3200, video_1080x1920).
- `2 - files\workflows\catalogo.py` = ponte output→input (o ComfyUI só lista arquivos de `input`): `pose`, `upscale`, `comparativo`, `lista`. Nunca apaga; versão anterior vira `.anterior-<data>`.
- Histórico dos testes (W1 v1, W2, W3a, W5 v1–v9, W6 v1): ver "Estado atual" e HISTORICO.md. Plano B não usado: Wan Animate 2.

## Inputs a preparar
- Vídeos: 1 pessoa, corpo inteiro, câmera parada, boa luz, ≥5 s, idealmente 24 fps, 9:16.
- Produto: foto de frente corpo inteiro, costas (se o vídeo tem giro), close da estampa/logo, descrição curta da peça.

## Estado atual (2026-11-22) — histórico dos testes
- W1 rodou OK com `fashion-lookbook-look-02-video.mp4` (724×1268, 30 fps, 150 frames) → pose 576×1024; saiu em `output/motion/catalogo/_teste_B4-P13/` (nome não foi trocado). Esqueletos completos (corpo, mãos, rosto, pés).
- W2 montado: `motion_W2_pose-em-imagem.json` (API em `2 - files\workflows\W2_api.json`, gerador `build_W2.py`). Klein 9B base, 480×848, 20 passos, CFG 3.5, seed fixa 20261121. Image 1 = produto (1 MP), image 2 = pose (0.5 MP), 4 ramos. Inputs em `input/motion/W2/look-02/`; produto é PROVISÓRIO (frame 1 do próprio vídeo). Saída `output/motion/W2/<nome>/pose-1..4`.
- Teste 1 (produto = frame do vídeo): roupa fiel, mas poses parecidas demais para avaliar aderência.
- Teste 2 (foto real: regata rosa + calça branca + camisa listrada na cintura): modelo/fundo/pose vieram da imagem nova, mas a ROUPA veio do texto antigo da descrição. Lição: texto da descrição vence a imagem 1. Corrigido: descrição agora opcional e vazia por padrão, prompt reforça "roupa só da imagem 1". Produto em `input/motion/W2/produtos/regata-rosa_frente.png`, nome `regata-rosa_look-02`.
- Teste 3 (descrição vazia): FUNCIONOU — roupa da imagem 1 na pose do esqueleto. Melhor saída: `output/motion/W2/look-02/pose-*_00004_.png`.
- W3a montado: `motion_W3a_anima-h3.json` (API em `2 - files\workflows\W3a_api.json`, gerador `build_W3a.py`). H3 ref2va + Fun ControlNet union (strength 1), BasicGuider (guidance 1.0), res_multistep, turbo LoRA 4 passos via switch, 480×864, 124 frames, 24 fps, seed fixa. Ref 1 = produto regata; primeiro quadro (MiniMaxH3AddGuide frame 0) = W2 pose-1_00004; control = `input/motion/W3a/look-02_pose.mp4` reamostrado com VideoFrameSample uniform 124. Saída `output/motion/W3a/<nome>/video_*.mp4`.
- Vídeo novo baixado (ainda não passou no W1): `3 - Assets\referencias de pose\pozze_black-friday_DfEy39VA9dX.mp4` (720×1280, 30 fps, 11 s; tem giro de costas; corta na coxa).
- W3a rodou (2ª tentativa; 1ª falhou no VAEDecode por bug do model_management do ComfyUI — IndexError em free_memory; re-rodar resolve, plano B = VAE Decode Tiled). Saída `output/motion/W3a/regata-rosa_look-02/video_00001_.mp4`.
- W4 feito como script Python (não é workflow ComfyUI): `2 - files\workflows\W4_lado_a_lado.py <original> <pose> <gerado> <saida>` — alinha por amostragem uniforme, rótulos, áudio do gerado. Saída `output/motion/W4/regata-rosa_look-02_lado-a-lado.mp4`.
- W1 já foi rodado no vídeo Pozze (saiu como `catalogo/_teste_B4-P13/pose_00002_.mp4` / `original_00002_.mp4`, 330 frames — nome não foi trocado).
- W3a aprovado como teste; partindo para qualidade.
- W5 qualidade v1→v6 (detalhes em `HISTORICO.md` #9–#21; geradores `build_W5*.py`). Aprendizados:
  - Quadro (Etapa 1): melhor = v3 — 1536×2720, produto 4 MP, **VAE `flux2-vae`** (decoder completo; o `full_encoder_small_decoder` deixa embaçado).
  - Vídeo (Etapa 2): VAE de vídeo fp16 baixado (v4) e esqueleto sem rosto (v5, `draw_face=False`, `draw_head=True`) não mudaram o rosto. A 704×1248 roupa fiel mas rosto deformado (rosto ~100 px). A 1088×1920 (v6) rosto bom mas **roupa trocada** e 59 min/vídeo → 1080p nativo no H3 local não é viável.
  - Agrupar/desligar etapas: botão direito no título do grupo → Set Group Nodes to Never/Always (nativo).
  - **v7 (896×1600) = melhor equilíbrio local:** roupa fiel, rosto bem melhor que a 704×1248, 18,6 min/vídeo (~51 s/passo, cabe na VRAM). Saída `output/motion/W5_v7/regata-rosa_look-02_q7/` (HISTORICO #23).
- W6 upscale v1 montado: `motion_W6_upscale_v1.json` (gerador `build_W6.py`), RelayVSR x2 local (modelos baixados), entrada `input/motion/W6/regata-rosa_look-02_q7.mp4` → `output/motion/W6_v1/<nome>/video_2x` (1792×3200) e `video_1080x1920`. Rodou: nitidez ok, mas mantém artefatos de rosto da geração (HISTORICO #24–#25).
- Replicabilidade (HISTORICO #26): W5 v7 com produto novo (`input/motion/W2/produtos/regata-caramelo-jeans_frente.png`) → roupa fiel, rosto bom, ~27 min; **bolsa na mão some no vídeo**. Saída `W5_v7/regata-rosa_look-02_q7/*_00002_*` (nome não foi trocado).
- Olho vesgo/fora do lugar: causa = pontos de cabeça do esqueleto (do vídeo original) não encaixam no rosto gerado (ficam acima) e o ControlNet puxa os olhos. **W5 v8** montado (`motion_W5_qualidade_v8`, `build_W5_v8.py`): `draw_head=False` no esqueleto do ControlNet, produto caramelo; saída `output/motion/W5_v8/regata-caramelo-jeans_look-02_q8/`. Ainda não rodado (HISTORICO #27).
- W5 v8 rodou e FALHOU (#28): sem cabeça o esqueleto vira linhas desenhadas na roupa → **nunca tirar a cabeça**.
- Pesquisa do rosto: `1 - AI instructions\pesquisa-olhos-pose-h3.md` (plano A afrouxar ControlNet → B retargeting da cabeça, de preferência só translação → C 2ª passada no rosto com inpaint nativo do H3).
- **W5 v9** montado (`motion_W5_qualidade_v9`, `build_W5_v9.py`, HISTORICO #29): v7 + ControlNet `end_percent` 0.7, produto caramelo. **Rodou (#30, 27,7 min): olhos melhores nos quadros de giro, roupa e movimento iguais à v7 → candidata a nova base.** Falta assistir o vídeo inteiro.
- Ferramentas fora do ComfyUI: `W4_lado_a_lado.py` (original|pose|gerado) e `W4_compara_versoes.py` (N versões lado a lado).
- **Produção montada (#33):** W1 v2 + W5 v10 + W6 v2 + catalogo.py. Nenhum rodou ainda. Teste sugerido: W1 v2 com look-02 → `catalogo.py pose look-02` → W5 v10 (deve sair parecido com a v9).
- **Base de produção = W5 v9** (`motion_W5_qualidade_v9`, aprovada pelo usuário em 2026-11-22, HISTORICO #31): v7 + ControlNet `end_percent` 0.7. Novas versões partem dela (`build_W5_v9.py`).
- Próximo: testar com outro produto/vídeo (Pozze) para confirmar replicabilidade; se ainda aparecer olho errado, testar end 0.6 ou o passo B (translação da cabeça do esqueleto); upscale para 1080p (W6) por cima da v9.
