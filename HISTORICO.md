# Histórico de alterações — Fashion pose-to-video

Registro detalhado do que foi criado ou alterado, onde, e por quê. A entrada mais nova fica no topo.
Caminhos abreviados:
- `WF/` = `D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI\user\default\workflows\` (workflows que aparecem no ComfyUI)
- `IN/` = `D:\Comfy-Desktop\ComfyUI-Shared\input\`
- `OUT/` = `D:\Comfy-Desktop\ComfyUI-Shared\output\`
- `PROJ/` = `E:\dev\Fashion-pose-to-video\`

**Regra de versionamento (a partir de 2026-11-21):** workflow existente não é mais alterado. Mudança de configuração = novo arquivo com sufixo de versão (`_v1`, `_v2`…), tanto no ComfyUI (`WF/`) quanto na cópia API e no gerador (`PROJ/2 - files/workflows/`). Os geradores `build_*.py` se recusam a sobrescrever um arquivo de versão existente.

---

## 2026-11-22 — #36 Projeto no GitHub (privado) + README
**Criado:** repositório git em `PROJ/` (branch `main`) e repositório **privado** https://github.com/LuanVelo/fashion-pose-to-video (pedido do usuário; privado por padrão, dá para tornar público em Settings).
- `README.md`: o que é, fluxo em Mermaid, os 3 workflows de produção, passo a passo, requisitos, **tabela dos 12 modelos com links originais** (os mesmos dos templates oficiais do ComfyUI) e árvore de `models/`, pastas de input/output, configuração da base, resultados e aprendizados com imagens.
- `docs/media/`: `exemplo_4-etapas.gif` (960 px, 12 fps, aparece direto no README), `exemplo_4-etapas.mp4` (2400 px, 2,3 MB), `pipeline.jpg`, `rosto_v7_x_v9.jpg`, `corpo_v7_x_v9.jpg`, `v8_x_v9.jpg`, `zoom_upscale.jpg`.
- `.gitignore`: modelos (`*.safetensors` etc.), vídeos de `3 - Assets/` (conteúdo de terceiros), `*.anterior-*`.
- `3 - Assets/referencias de pose/LEIA-ME.md`: explica que os vídeos não sobem.
**Não sobe:** modelos, vídeos de referência, saídas do ComfyUI (só os exemplos em `docs/media`).
**Daqui em diante:** cada mudança registrada aqui vira um commit + push.

## 2026-11-22 — #35 Comparativo das 4 etapas + opções no W4_compara_versoes.py
**Alterado:** `PROJ/2 - files/workflows/W4_compara_versoes.py` — antes: altura = maior vídeo e nº de quadros = do 1º vídeo → depois: opções `--altura=N` e `--frames=N` (sem elas, igual a antes). Motivo: 4 painéis a 1920 px passariam de 4.300 px de largura (muitos players não tocam); e o original tem 150 quadros, os outros 124.
**Criado:** `OUT/motion/producao/regata-caramelo-jeans_look-02/lado-a-lado_4-etapas.mp4` (3634×1644, 124 quadros, 24 fps, sem áudio): 1 ORIGINAL (`catalogo/_teste_B4-P13/original_00001_.mp4`) | 2 ESQUELETO (v9 `pose_sem-rosto_00001_`) | 3 GERADO 896x1600 (v9 `video_00001_`) | 4 SUPER-RESOLUÇÃO 1080x1920 (W6 v2). Painéis a 1600 px (altura nativa do gerado).
**Nenhum workflow alterado.**

## 2026-11-22 — #34 W6 v2 executada com o vídeo da v9 — upscale bom
Rodada pelo usuário com entrada `IN/video_00001_.mp4` (subida pela UI; idêntica a `OUT/motion/W5_v9/regata-caramelo-jeans_look-02_q9/video_00001_.mp4`). **0,8 min**, sem erro. Saídas em `OUT/motion/producao/regata-caramelo-jeans_look-02/`: `video_2x_00001_.mp4` (1792×3200) e `video_1080x1920_00001_.mp4`.
**Conferência:** `zoom_upscale.png` na mesma pasta (quadro 60, rosto e regata, original × 2x).
- Rosto: bem mais nítido (cílios, sobrancelhas, lábios, cabelo); olhos continuam certos (o defeito da v7 não existe na v9, então o upscale não tem o que ampliar).
- Tecido: trama de tricô da regata bem marcada (o produto é tricô, então é coerente), jeans e costura mais definidos.
- Efeito colateral: um pouco mais de contraste e saturação na pele e sobrancelhas mais escuras. Se incomodar: `detail` 0,7 no VSR Decode (seria W6 v3).
**Lado a lado (pedido do usuário: toda comparação vira vídeo simultâneo):** `lado-a-lado_upscale.mp4` (quadro inteiro, 896x1600 x 1080x1920, via W4_compara_versoes.py) e `lado-a-lado_upscale_zoom.mp4` (rosto e regata em zoom, recorte seguindo o nariz do esqueleto com média móvel de 9 quadros), na mesma pasta.
**Conclusão (minha avaliação; aguardando o usuário):** v9 + W6 v2 funciona como fluxo completo. Nenhum workflow alterado.

## 2026-11-22 — #33 Fluxo de produção em 3 workflows + limpeza do ComfyUI
**Pedido do usuário:** catálogo com ~4 poses → separar a extração de pose da geração. 3 workflows de produção no ComfyUI; testes arquivados no projeto e removidos do ComfyUI.
**Criado (geradores e API em `PROJ/2 - files/workflows/`; UI em `WF/` com cópia em `ui_producao/`; as três conferidas: API da UI = gerador, recarregadas do disco):**
- `motion_W1_extrai-pose_v2` (`build_W1_v2.py`, `W1_extrai-pose_v2_api.json`). Antes (v1) → depois: esqueleto com rosto, fps nativo, trecho em frames, SDPose em todos os quadros → **sem rosto e com cabeça (igual W5 v9), trecho em segundos convertido pelo fps do vídeo (`ComfyMathExpression` round(a*b)), reamostra para 124 quadros antes do SDPose, salva a 24 fps**; original salvo com os mesmos 124 quadros (sem áudio). Duração padrão 5,2 s (a UI arredonda a 0,1). Saída igual: `OUT/motion/catalogo/<pose>/`.
- `motion_W5_qualidade_v10` (`build_W5_v10.py`, `W5_qualidade_v10_api.json`). Antes (v9) → depois: LoadVideo do vídeo original + SDPose (nós 210, 230–237) e LoadImage `pose-1.png` (109) → **LoadVideo `motion/poses/<pose>/pose.mp4` (210) + `ImageFromBatch` índice 0 (240) como pose do primeiro quadro**; saída `motion/W5_v9/` → **`motion/producao/<nome>/`**. Resto idêntico (end 0.7, 896×1600, seeds). Diferença esperada vs v9: a pose do primeiro quadro agora vem sem pontos de rosto (o pose-1.png do W1 v1 tinha) e o pose.mp4 passa por compressão de vídeo.
- `motion_W6_upscale_v2` (`build_W6_v2.py`, `W6_upscale_v2_api.json`). Antes (v1) → depois: entrada `motion/W6/...` e saída `motion/W6_v1/` → **entrada `motion/producao/<nome>.mp4`, saída `motion/producao/<nome>/`**; seed do KSampler fixada em 42 ("fixed"; o front sorteava ao abrir). Qualidade igual.
- `catalogo.py`: `pose <pose>` (OUT/catalogo → IN/motion/poses/<pose>/pose.mp4, original.mp4, keyframes), `upscale <nome>` (OUT/producao/<nome>/video_* → IN/motion/producao/<nome>.mp4), `comparativo <nome> <pose>` (W4 → OUT/producao/<nome>/comparativo.mp4), `lista`. Não apaga; substituído vira `.anterior-<data>`.
**Movido (copiado, conferido byte a byte com `cmp` e removido de `WF/`):** `motion_W1_extrai-pose`, `motion_W2_pose-em-imagem`, `motion_W3a_anima-h3`, `motion_W5_qualidade_v1`…`v9`, `motion_W6_upscale_v1` → `PROJ/2 - files/workflows/ui_testes/`. Removidas também as pastas auxiliares `user/default/motion_api/` e `tmp_api/` (idênticas às cópias API do projeto). Workflows de outros projetos (vovo, h3, rioopen) não foram tocados.
**Status:** nenhum dos 3 rodou ainda.

## 2026-11-22 — #32 Comparativo da v9 + página de apresentação do projeto
**Criado:** `OUT/motion/W4/regata-caramelo-jeans_look-02_q9_lado-a-lado.mp4` (1480×904, 124 frames, 24 fps, com áudio), via `W4_lado_a_lado.py` com original = `OUT/motion/catalogo/_teste_B4-P13/original_00001_.mp4`, esqueleto e vídeo da W5 v9.
**Criado:** página (artefato privado) que explica o projeto, com o comparativo, o pipeline, os workflows, a configuração da v9, o histórico v1→v9, o problema do rosto, os aprendizados e os próximos passos: https://claude.ai/artifact/MSZTy9bCannn73yKp5SSrC . Fonte e imagens no scratchpad da sessão.
**Nenhum workflow alterado.**

## 2026-11-22 — #31 W5 v9 aprovada como base de produção
**Decisão do usuário:** a v9 (`WF/motion_W5_qualidade_v9.json`, `PROJ/2 - files/workflows/build_W5_v9.py`) substitui a v7 como base. Antes → depois: base v7 (ControlNet end 1.0) → **v9 (end 0.7)**. Motivo: olhos melhores nos giros de cabeça sem perder roupa, movimento nem tempo (#30). Nenhum arquivo de workflow alterado; v7 e v8 ficam como histórico. Próximas versões partem da v9.

## 2026-11-22 — #30 W5 v9 executada — olhos melhores, roupa e movimento iguais à v7
Rodou sem erro: **27 min 40 s** (frame0 em ~7 min; vídeo ~20 min). Saídas em `OUT/motion/W5_v9/regata-caramelo-jeans_look-02_q9/`: `video_00001_.mp4`, `frame0_00001_.png`, `pose_sem-rosto_00001_.mp4`.
**Conferência** (script `confere_v9.py` no scratchpad; rodado só depois do fim do render): `corpo.png` (quadros 0/30/60/90/123) e `rosto.png` (12 quadros, recorte seguindo o nariz do esqueleto), v7 `_00002_` (end 1.0) × v9 (end 0.7), mesma seed e produto. Ambos na pasta de saída.
**Resultado:**
- Movimento: poses idênticas à v7 nos 5 quadros → soltar os 30% finais não fez perder o movimento.
- Roupa: regata caramelo e jeans fiéis, iguais à v7.
- Rosto: na v7, os quadros 44–77 (cabeça virando) têm um olho mais fechado/assimétrico; na v9 os olhos ficam abertos, simétricos e no lugar em todos os 12 quadros amostrados. Sobrancelhas e traços mais próximos do frame0.
- Limite: avaliados 12 de 124 quadros; falta assistir o vídeo inteiro.
**Conclusão:** `end_percent 0.7` melhora o olho sem custo de roupa, movimento nem tempo. Candidata a nova base no lugar da v7. Se ainda aparecer olho errado no vídeo inteiro: testar end 0.6.

## 2026-11-22 — #29 W5 qualidade v9 (cabeça de volta + ControlNet end_percent 0.7)
**Motivo:** passo A da pesquisa `PROJ/1 - AI instructions/pesquisa-olhos-pose-h3.md`. A cabeça do esqueleto (do vídeo original) não encaixa no rosto gerado e o ControlNet puxa os olhos; tirar a cabeça (v8) quebrou tudo. Hipótese: os passos iniciais fixam layout/movimento e os finais fazem o detalhe do rosto → soltar o ControlNet nos 30% finais deixa o rosto seguir o primeiro quadro. Conferido no código (`comfy_extras/nodes_minimax_h3.py`): `start_percent`/`end_percent` existem no `MiniMaxH3FunControlNetApply` (campos "advanced" na UI). Patch instalado = Union v1.
**Criado (v7 e v8 intactas):** `WF/motion_W5_qualidade_v9.json` (partiu da v8 na UI, grupos mantidos, nota reescrita), `PROJ/2 - files/workflows/build_W5_v9.py` e `W5_qualidade_v9_api.json` (conferido: API da UI = gerador).

**Diferenças v7 → v9** (produto igual ao teste #26):
| Nó | v7 (_00002_, teste #26) | v9 |
|---|---|---|
| Nome do teste (1) / Pasta (2) | regata-rosa_look-02_q7 / motion/W5_v7/ | regata-caramelo-jeans_look-02_q9 / motion/W5_v9/ |
| ControlNet (214) `end_percent` | 1.0 | **0.7** (strength 1.0, start 0) |
| SDPoseDrawKeypoints (234) | draw_face=False, draw_head=True | igual (v8 tinha draw_head=False) |

Mantido 124 frames (não clipe curto) para comparar direto com `OUT/motion/W5_v7/regata-rosa_look-02_q7/video_00002_.mp4` (mesmo produto, mesma seed) sem precisar rodar uma base nova.
**Avaliar:** olhos (posição/vesgo), fidelidade da roupa, fidelidade do movimento. Próximos da matriz se precisar: end 0.6; strength 0.8/end 1.0; strength 0.8/end 0.7.
**Saída:** `OUT/motion/W5_v9/regata-caramelo-jeans_look-02_q9/`. **Tempo estimado:** ~27 min. **Status:** montado, não executado.

## 2026-11-22 — #28 W5 v8 executada — FALHOU: esqueleto sem cabeça virou "desenho" na roupa
Rodou sem erro técnico: **26 min 23 s** (Etapa 1 7 min 19 s a 15,7 s/passo; vídeo 17 min 29 s a 52,4 s/passo). Saídas em `OUT/motion/W5_v8/regata-caramelo-jeans_look-02_q8/`: `video_00001_.mp4`, `pose_sem-cabeca_00001_.mp4`, `frame0_00001_.png`.
**Resultado:** as linhas do esqueleto foram desenhadas NA ROUPA em todo o vídeo — barra nos ombros, linhas do pescoço ao quadril na regata, costuras verticais no jeans e "mangas" translúcidas seguindo os braços. Rosto ok, mas o vídeo é inutilizável.
**Causa provável:** o Fun ControlNet *union* deduz o tipo de controle pela imagem. Sem cabeça, o boneco deixa de parecer um esqueleto de pose e passa a ser lido como mapa de bordas/linhas (canny/lineart), então o modelo copia as linhas como contornos.
**Lição:** a cabeça precisa ficar no esqueleto (`draw_head=True`). Para o olho, mexer em força/duração do ControlNet e não no desenho.
Comparativo: scratchpad `v8_check.png` (enviado no chat).

## 2026-11-21 — #27 W5 qualidade v8 (esqueleto do ControlNet SEM cabeça)
**Motivo (análise do olho vesgo/fora do lugar):** sobrepondo o esqueleto ao vídeo, no ORIGINAL os pontos de olhos/nariz encaixam exatamente; no GERADO o rosto fica mais baixo e maior — os pontos dos "olhos" caem nas sobrancelhas e o "nariz" entre os olhos. O H3 recebe sinais conflitantes (primeiro quadro/ref dizem uma altura de olho, ControlNet força 1.0 diz outra) e em alguns quadros o olho escorrega ou desalinha. O desencaixe nasce na Etapa 1 (Klein não põe a cabeça exatamente nos pontos) e na diferença de proporção entre pessoas. Imagem da análise: scratchpad `esq_original_vs_gerado.png` (enviada no chat).
**Criado (v7 intacta):** `WF/motion_W5_qualidade_v8.json` (partiu da v7 na UI, grupos e nota mantidos), `PROJ/2 - files/workflows/build_W5_v8.py` e `W5_qualidade_v8_api.json` (conferido: API da UI = gerador).

**Diferenças v7 → v8:**
| Nó | v7 | v8 |
|---|---|---|
| Nome do teste (1) / Pasta (2) | regata-rosa_look-02_q7 / motion/W5_v7/ | regata-caramelo-jeans_look-02_q8 / motion/W5_v8/ |
| Produto (5) | motion/W2/produtos/regata-rosa_frente.png | motion/W2/produtos/regata-caramelo-jeans_frente.png |
| SDPoseDrawKeypoints (234) `draw_head` | True | **False** (sem olhos/nariz/orelhas; corpo, mãos e pés iguais) |
| Prefixo pose (235) | /pose_sem-rosto | /pose_sem-cabeca |

**Risco:** giro de cabeça do vídeo original deixa de ser imposto (só pescoço/ombros guiam). Se perder movimento de cabeça → alternativa: cabeça ligada + ControlNet `end_percent` 0.5.
**Comparar com:** `OUT/motion/W5_v7/regata-rosa_look-02_q7/video_00002_.mp4` (mesmo produto, mesma seed). **Status:** montado, não executado.

## 2026-11-21 — #26 W5 v7 com produto novo (regata caramelo + jeans) — replicabilidade
**Sem alteração de workflow:** só trocou a foto do produto (`IN/image (2).png`, 1920×2720; cópia organizada em `IN/motion/W2/produtos/regata-caramelo-jeans_frente.png`). Nome do teste NÃO foi trocado → saídas `_00002_` em `OUT/motion/W5_v7/regata-rosa_look-02_q7/` (`frame0_00002_.png`, `video_00002_.mp4`, `pose_sem-rosto_00002_.mp4`).
**Tempo:** 27 min 13 s no total (vídeo 17 min 22 s, ~52 s/passo; etapa 1 refeita com produto novo).
**Criado:** `check_caramelo_corpo.png` (produto | frame0 | quadros 0/30/60/90/123) e `zoom_rosto_caramelo.png`, na mesma pasta.
**Avaliação:**
- Regata tricô caramelo, jeans azul wide e chinelo preto: **fiéis** no vídeo todo. Decote saiu mais em U do que em V. Jeans com algumas manchas escuras estranhas em alguns quadros.
- **Bolsa tote de camurça: aparece no frame0, mas SOME no vídeo desde o quadro 0** (o esqueleto não tem bolsa e o movimento das mãos não a sustenta). Fundo do vídeo também ficou mais cinza que o frame0.
- Rosto: natural e estável, sem os artefatos da modelo anterior; cabelo cacheado bem mantido. Identidade muda um pouco em relação ao produto (já no frame0).
- **Conclusão:** o pipeline é replicável para roupa; acessórios carregados na mão (bolsa) não são mantidos.

## 2026-11-21 — #25 W6 v1 executada — upscale ok, mas mantém os artefatos do rosto
Rodou e salvou `OUT/motion/W6_v1/regata-rosa_look-02_q7/video_2x_00001_.mp4` (1792×3200) e `video_1080x1920_00001_.mp4`. Zoom comparativo (v7 × upscale): mais nitidez, mas os defeitos de olhos/pálpebra da v7 continuam — upscale não corrige rosto; o problema está na geração (H3 a 896×1600).
Ideias registradas (não feitas): 2ª passada H3 em 1088×1920 com denoise parcial sobre a v7 (precisa confirmar suporte nos nós nativos); referência de rosto em close como 2ª ref.

## 2026-11-21 — #24 W6 upscale de vídeo v1 (RelayVSR x2, local)
**Motivo:** levar o vídeo da v7 (896×1600) a 1080p/2K sem regenerar, rodando local.
**Baixado (autorizado pelo usuário):** `models/diffusion_models/relayvsr_x2_lightx2v_int8_convrot.safetensors` (4,81 GB) e `models/vae/relayvsr_flash_vae_x2_fp32.safetensors` (122 MB), de Comfy-Org/RelayVSR. Par x2 retreinado pela LightX2V para vir depois do H3.
**Criado:** `WF/motion_W6_upscale_v1.json`, `PROJ/2 - files/workflows/build_W6.py` e `W6_upscale_v1_api.json`. Base: template oficial `utility_relayvsr_video_x2_upscale` (subgrafo aberto em nós nativos).
**Entrada:** `IN/motion/W6/regata-rosa_look-02_q7.mp4` (cópia de `OUT/motion/W5_v7/regata-rosa_look-02_q7/video_00001_.mp4`).
**Fluxo:** LoadVideo → GetVideoComponents → RelayVSRConditioning → KSampler (1 passo, cfg 1, euler/simple, seed 42) → VSRDecode (detail 1.0) → CreateVideo (áudio e fps da entrada) → salva `video_2x` (1792×3200) + ImageScale lanczos crop center → salva `video_1080x1920`.
**Saída:** `OUT/motion/W6_v1/<nome>/`. **Ajuste se inventar detalhe:** baixar `detail` do VSR Decode (ex. 0,7) → seria v2.
**Status:** montado, não executado.

## 2026-11-21 — #23 W5 v7 executada — roupa fiel, rosto melhor; 18,6 min
Rodou sem erro: **18 min 38 s** no total (vídeo 20 passos em 17 min 10 s, **~51,5 s/passo**, coube na VRAM, sem o offload da v6). Saídas em `OUT/motion/W5_v7/regata-rosa_look-02_q7/`: `video_00001_.mp4` (896×1600, 124 frames), `pose_sem-rosto_00001_.mp4`, `frame0_00001_.png`.
**Criado:** `comparativo_v5_v6_v7.mp4` (3 vídeos lado a lado, via `W4_compara_versoes.py`) e `zoom_rosto_v5_v6_v7.png` (rosto nos quadros 0/40/82/123 + entrada), na mesma pasta.
**Avaliação:**
- Roupa: **fiel** em todos os quadros (regata rosa decote V, calça branca, camisa listrada vermelha amarrada na cintura, sandália) — diferente da v6.
- Rosto: mais natural e estável que na v5 (704×1248); ainda um pouco menos detalhado que na v6 (1088×1920). Giro de cabeça (quadro ~82) sai coerente.
- **Conclusão:** 896×1600 é o melhor equilíbrio local até agora (qualidade × fidelidade × tempo).

## 2026-11-21 — #22 W5 qualidade v7 (vídeo em 896×1600)
**Motivo:** buscar o meio-termo entre v5 (704×1248: roupa fiel, rosto deformado) e v6 (1088×1920: rosto bom, roupa trocada, 59 min).
**Criado (v1–v6 intactas):** `WF/motion_W5_qualidade_v7.json` (partiu da v6), `PROJ/2 - files/workflows/build_W5_v7.py` e `W5_qualidade_v7_api.json`.

**Diferenças v6 → v7:**
| Nó | v6 | v7 |
|---|---|---|
| Nome do teste (1) / Pasta (2) | …_q6 / motion/W5_v6/ | …_q7 / motion/W5_v7/ |
| MiniMaxH3ReferenceToVideo (216) width × height | 1088 × 1920 | **896 × 1600** (~1,4 MP) |

Resto idêntico (quadro 1536×2720 flux2-vae, esqueleto sem rosto, 20 passos, ref max, VAE de vídeo fp16, seed 20261121).
**Tempo estimado:** 20–30 min (não medido). **Status:** montado, não executado.

## 2026-11-21 — #21 W5 v6 executada — rosto natural, mas a ROUPA mudou; 59 min
Sem erro de memória, mas **59 min 24 s** (20 passos a ~180 s/passo, contra ~25 s a 704×1248 — sinal de offload de VRAM para RAM). Saídas em `OUT/motion/W5_v6/regata-rosa_look-02_q6/`: `video_00001_.mp4` (1088×1920, 124 frames), `pose_sem-rosto_00001_.mp4`, `frame0_00001_.png`.
**Criado:** `comparativo_v5_x_v6.mp4`, `zoom_rosto_v5_x_v6.png` na mesma pasta.
**Avaliação:**
- **Rosto: muito melhor** — natural, expressões reais, sem a deformação de v1–v5. Confirma que o problema do rosto era falta de pixels.
- **Roupa: regressão grave** — desde o frame 0 a regata virou **suéter de manga longa com gola redonda**, e a camisa listrada amarrada virou **saia listrada** por cima da calça. O H3 ignorou o primeiro quadro (AddGuide) e a referência do produto nessa resolução.
- Hipótese: 1088×1920 está fora da faixa de treino do H3 local (~0,9 MP); acima dela a adesão às referências cai.
**Conclusão:** 1080p nativo no H3 local não é viável (roupa errada + 1 h por vídeo). Resolução ideal fica entre 704×1248 (roupa fiel, rosto ruim) e 1088×1920 (rosto bom, roupa errada).
**Nenhum workflow alterado.**

## 2026-11-21 — #20 W5 qualidade v6 (vídeo em 1088×1920)
**Motivo:** o rosto deforma já no frame 0 (ancorado no quadro em alta) → falta de pixels: a 704×1248 o rosto tem ~100 px de largura. Referência de rosto em close fica para depois (não adiciona pixels).
**Criado (v1–v5 intactas):** `WF/motion_W5_qualidade_v6.json` (partiu da v5), `PROJ/2 - files/workflows/build_W5_v6.py` e `W5_qualidade_v6_api.json`.

**Diferenças v5 → v6:**
| Nó | v5 | v6 |
|---|---|---|
| Nome do teste (1) / Pasta (2) | …_q5 / motion/W5_v5/ | …_q6 / motion/W5_v6/ |
| MiniMaxH3ReferenceToVideo (216) width × height | 704 × 1248 | **1088 × 1920** (~2,1 MP; rosto ~2,4× mais pixels) |

Resto idêntico à v5 (quadro 1536×2720 flux2-vae, esqueleto sem rosto, 20 passos, ref max, VAE de vídeo fp16, seed 20261121).
**Risco:** tempo estimado 25–40 min (não medido) e possível falta de VRAM → fallback v7 em 896×1600.
**Status:** montado, não executado.

## 2026-11-21 — #19 W5 v5 executada — esqueleto sem rosto não resolveu o rosto
Sem erro; **584 s** (Etapa 1 do cache; extração do esqueleto + 20 passos em 8 min 28 s). Saídas em `OUT/motion/W5_v5/regata-rosa_look-02_q5/`: `frame0_00001_.png`, `pose_sem-rosto_00001_.mp4` (124 frames, 576×1024), `video_00001_.mp4`.
**Criado:** `comparativo_v1_v4_v5.mp4` e `zoom_rosto_v1_v4_v5.png` na mesma pasta.
**Avaliação (zoom do rosto, frames 0/40/82/123):** v1, v4 e v5 praticamente iguais — rosto mais magro/marcado que a entrada e mudando ao longo do vídeo. **Hipótese dos landmarks de rosto descartada** (efeito pequeno ou nulo). Também já descartados: VAE de imagem (v3 resolveu só o quadro) e VAE de vídeo (v4).
**Hipóteses restantes:** (1) rosto pequeno demais no quadro do vídeo (~100 px de largura a 704×1248); (2) H3 sem referência de rosto em close (só a foto de corpo inteiro).
**Nenhum workflow alterado.**

## 2026-11-21 — #18 W5 qualidade v5 (esqueleto sem rosto)
**Pedido:** partir da v4 e alterar só o esqueleto, tirando o rosto. Dúvida do usuário: a cabeça ficaria sem controle? **Não:** no código do ComfyUI (`comfy_extras/pose/keypoint_draw.py`) `draw_head` (nariz, olhos, orelhas = posição/rotação da cabeça) é independente de `draw_face` (68 pontos de contorno, boca, sobrancelhas). v5 usa `draw_face=False` e `draw_head=True`.
**Criado (v1–v4 intactas):**
- `WF/motion_W5_qualidade_v5.json` (posições e grupos copiados da v4 + novo grupo "ETAPA 2a")
- `PROJ/2 - files/workflows/build_W5_v5.py` e `W5_qualidade_v5_api.json` (+ cópia em `...\user\default\motion_api\`)

**Diferenças v4 → v5:**
| Nó | v4 | v5 |
|---|---|---|
| Nome do teste (1) / Pasta (2) | …_q4 / motion/W5_v4/ | …_q5 / motion/W5_v5/ |
| LoadVideo (210) | `motion/W3a/look-02_pose.mp4` (esqueleto pronto do W1, com rosto) | `fashion-lookbook-look-02-video.mp4` (**vídeo original**) |
| Novos 230–234 | — | SDPose dentro da Etapa 2: checkpoint sdpose → resize 1024 → grid 32 → extractor (batch 16) → **draw: body, hands, feet, head ON; face OFF**; traço 4, limiar 0.5 (= W1) |
| Novos 235–237 | — | salva o esqueleto sem rosto: `OUT/motion/W5_v5/<nome>/pose_sem-rosto_*.mp4` (24 fps) — registro replicável |
| ControlNet (214) `control_video` | frames do pose.mp4 do W1 | saída do draw sem rosto (234) |

Resto idêntico à v4 (quadro 1536×2720 com flux2-vae; vídeo 704×1248, 20 passos, ref max, VAE de vídeo fp16, seed 20261121).
**Status:** montado, não executado.

## 2026-11-21 — #17 W5 v4 executada — rosto ruim no vídeo
Etapa 1 veio do cache (quadro igual à v3); Etapa 2 sem erro, **581 s** (20 passos em 8 min 25 s). Saídas em `OUT/motion/W5_v4/regata-rosa_look-02_q4/`: `frame0_00001_.png`, `video_00001_.mp4`.
**Criado:** `PROJ/2 - files/workflows/W4_compara_versoes.py` (N vídeos lado a lado com rótulos); `comparativo_v1_x_v4.mp4` e `zoom_rosto_v1_x_v4.png` na pasta de saída da v4.
**Avaliação (usuário: "rosto ficou péssimo"; confirmado no zoom):**
- v1 e v4 têm o rosto praticamente igual de ruim → **o VAE fp16 não resolveu o rosto**; o problema está antes do decode.
- Já no frame 0 o rosto difere do quadro de entrada (olhos assimétricos, rosto mais magro/marcado) e muda ao longo do vídeo (perde identidade).
- Hipóteses: (1) **landmarks de rosto do esqueleto** (SDPose `draw_face=true`) vêm do rosto da modelo ORIGINAL e forçam esse formato num rosto diferente; (2) **rosto pequeno**: ~100 px de largura num vídeo 704×1248; (3) H3 só tem a foto de corpo inteiro como referência de identidade.
**Nenhum workflow alterado.**

## 2026-11-21 — #16 Download do VAE de vídeo fp16 + W5 qualidade v4
**Baixado (autorizado pelo usuário):** `D:\Comfy-Desktop\ComfyUI-Shared\models\vae\minimax_h3_video_vae_fp16.safetensors` — 5.207.808.496 bytes (~5,21 GB), de `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors`.
**Conferência:** 562 tensores, todos F16. O antigo `int8_convrot` tem 850 tensores com 144 I8 + 144 U8 (pesos quantizados).
**Criado (v1–v3 intactas):**
- `WF/motion_W5_qualidade_v4.json` (partiu do layout da v3; **Etapa 2 ligada**)
- `PROJ/2 - files/workflows/build_W5_v4.py` e `W5_qualidade_v4_api.json`

**Diferenças v3 → v4:**
| Nó | v3 | v4 |
|---|---|---|
| Nome do teste (1) | regata-rosa_look-02_q3 | regata-rosa_look-02_q4 |
| Pasta base (2) | motion/W5_v3/ | motion/W5_v4/ |
| VAELoader de vídeo (202) | minimax_h3_video_vae_int8_convrot.safetensors | **minimax_h3_video_vae_fp16.safetensors** |
| Grupo Etapa 2 | Never | **Always** |

Etapa 1 idêntica à v3 (quadro 1536×2720, flux2-vae). Etapa 2 igual à v1 exceto o VAE e o quadro de entrada: 704×1248, 124 frames, 20 passos, ref max, ControlNet 1.0, seed 20261121.
**Comparar com:** vídeo da v1 (`OUT/motion/W5_v1/regata-rosa_look-02_q1/video_00001_.mp4`). Diferenças: quadro em alta (v3) + VAE de vídeo completo.
**Saída:** `OUT/motion/W5_v4/regata-rosa_look-02_q4/`. **Status:** montado, não executado.

## 2026-11-21 — #15 W5 v3, Etapa 1 executada — VAE completo aprovado
Usuário: "melhorou muito". Saída `OUT/motion/W5_v3/regata-rosa_look-02_q3/frame0_00001_.png` (1536×2720).
Comparação 1:1 do rosto v2 × v3: v3 com fios de cabelo, olhos e textura de pele definidos; v2 tinha manchas/artefatos do decoder reduzido. (A variância do Laplaciano não mudou — 35 → 34 — porque os artefatos da v2 também contavam como "alta frequência"; a métrica não serve para esse caso, vale a avaliação visual.)
**Lição:** decoder do VAE é gargalo de nitidez. O vídeo usa `minimax_h3_video_vae_int8_convrot` (quantizado, 2,62 GB); existe `minimax_h3_video_vae_fp16` (5,21 GB, Comfy-Org/MiniMax-H3), não baixado.
**Nenhum workflow alterado.**

## 2026-11-21 — #14 Download do VAE completo + W5 qualidade v3
**Baixado (autorizado pelo usuário):** `D:\Comfy-Desktop\ComfyUI-Shared\models\vae\flux2-vae.safetensors` — 336.213.556 bytes (~320,6 MB), de `https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors` (link usado em 20 templates oficiais).
**Conferência:** encoder idêntico ao `full_encoder_small_decoder` (137,7 MB); **decoder 198,5 MB vs 111,8 MB** no reduzido → confirma que o VAE antigo tem decoder leve.
**Criado (v1 e v2 intactas):**
- `WF/motion_W5_qualidade_v3.json` (partiu do layout da v2; Etapa 2 em Never)
- `PROJ/2 - files/workflows/build_W5_v3.py` e `W5_qualidade_v3_api.json`

**Diferenças v2 → v3:**
| Nó | v2 | v3 |
|---|---|---|
| Nome do teste (1) | regata-rosa_look-02_q2 | regata-rosa_look-02_q3 |
| Pasta base (2) | motion/W5_v2/ | motion/W5_v3/ |
| VAELoader da Etapa 1 (102) | full_encoder_small_decoder.safetensors | **flux2-vae.safetensors** |

Todo o resto idêntico (1536×2720, 28 passos, CFG 3.5, seed, produto 4 MP). Isola o efeito do VAE.
**Saída:** `OUT/motion/W5_v3/regata-rosa_look-02_q3/frame0_*.png`. **Status:** montado, não executado.
**Observação:** os outros workflows klein (W2, vovo_*, rioopen_*) continuam com o VAE reduzido; trocar só se o teste confirmar ganho.

## 2026-11-21 — #13 W5 v2, Etapa 1 executada — quadro ainda "embaçado"
Sem erro; **459 s** (~7 min 40 s) para o quadro 1536×2720. Saída `OUT/motion/W5_v2/regata-rosa_look-02_q2/frame0_00001_.png`.
**Medição de nitidez (variância do Laplaciano):** reduzidas a 768 px de largura → produto 113 · v2 98 · v1 70 (v2 bem melhor que v1). Na resolução nativa → produto 110 · **v2 35** → a 1:1 a v2 tem pouco detalhe por pixel: pele lisa, bordas macias (o "embaçado" que o usuário viu).
**Causa provável:** o VAE `full_encoder_small_decoder.safetensors` usado em todos os workflows klein tem **decoder reduzido** (versão leve). Os templates oficiais usam também o `flux2-vae.safetensors` (decoder completo, 320,6 MB, Comfy-Org no Hugging Face), **não baixado**. Fator secundário: 4 MP está no limite do klein.
**Criado:** `OUT/motion/W5_v2/regata-rosa_look-02_q2/zoom_v1_vs_v2.png` (recortes de rosto e trama).
**Nenhum workflow alterado.** Próximo teste proposto: v3 = v2 trocando só o VAE para `flux2-vae` (depende de autorização de download).

## 2026-11-21 — #12 W5 qualidade v2 (primeiro quadro na melhor qualidade)
**Motivo:** o vídeo local saiu com qualidade baixa; o primeiro quadro (que ancora o vídeo) estava em 704×1248. Foco agora: quadro na melhor qualidade possível; vídeo fica para depois.
**Criado (v1 intacta):**
- `WF/motion_W5_qualidade_v2.json` (partiu do layout da v1; Etapa 2 já salva em **Never**)
- `PROJ/2 - files/workflows/build_W5_v2.py` e `W5_qualidade_v2_api.json`
- cópia em `...\user\default\motion_api\W5_qualidade_v2_api.json`

**Diferenças v1 → v2 (somente Etapa 1 e nome):**
| Nó | v1 | v2 |
|---|---|---|
| Nome do teste (1) | regata-rosa_look-02_q1 | regata-rosa_look-02_q2 |
| Pasta base (2) | motion/W5_v1/ | motion/W5_v2/ |
| Produto (107, ImageScaleToTotalPixels) | 2 MP | **4 MP** |
| Esqueleto (110) | 0.9 MP | 1 MP |
| Flux2Scheduler (118) / EmptyFlux2LatentImage (119) | 704×1248 | **1536×2720** (~4,2 MP, teto prático do klein) |
| Grupo Etapa 2 | Always | Never (ligar quando for testar vídeo) |

Mantidos: 28 passos, CFG 3.5, euler, seed 20261121, prompt, descrição vazia. Etapa 2 idêntica à v1 (704×1248; o H3 reduz o quadro no AddGuide).
**Saída:** `OUT/motion/W5_v2/regata-rosa_look-02_q2/frame0_*.png`. **Status:** montado, não executado.

## 2026-11-21 — #11 W5 v1, Etapa 2 (vídeo em qualidade) executada
Etapa 2 religada com "Set Group Nodes to Always"; Etapa 1 veio do cache. Sem erro (o bug do VAEDecode não apareceu).
**Tempo:** 560 s no total (~9 min 20 s): carga do text encoder 32B ~20 s; amostragem **20 passos em 8 min 18 s (~24,9 s/passo)**; decode ~12 s. Referência para próximos vídeos 704×1248, 124 frames, ref max.
**Saída:** `OUT/motion/W5_v1/regata-rosa_look-02_q1/video_00001_.mp4` (704×1248, 24 fps, 124 frames, 5,17 s, com áudio).
**Criado:** `OUT/motion/W5_v1/regata-rosa_look-02_q1/comparativo_lado-a-lado.mp4` (via `W4_lado_a_lado.py`; painéis reduzidos a 864 px de altura — para nitidez, ver o vídeo sozinho).
**Avaliação inicial (4 frames):** roupa e identidade estáveis, pose segue o esqueleto. A "aproximação" do enquadramento que eu apontei como problema **está no vídeo original** (correção levantada pelo usuário e confirmada por medição no pose.mp4): a figura ocupa 65% da altura do quadro no frame 0, 72% no 37, 81% nos frames 75–112 e 78% no 149 (+25%; a modelo vem em direção à câmera). O H3 reproduziu fielmente — **não é defeito**. Ajustes de "travar câmera" descartados.
**Nenhum workflow alterado.**

## 2026-11-21 — #10 W5 v1, Etapa 1 executada
Rodada pelo usuário com a Etapa 2 em "Set Group Nodes to Never" (mute nativo do grupo, botão direito no título). Sem erro; 128 s no total (28 passos em 1 min 49 s, ~3,9 s/passo).
**Saída:** `OUT/motion/W5_v1/regata-rosa_look-02_q1/frame0_00001_.png` (704×1248).
**Criado:** `OUT/motion/W5_v1/regata-rosa_look-02_q1/comparativo_frame0.png` (produto | esqueleto | gerado, feito com PIL, fora do ComfyUI).
**Avaliação:** roupa fiel (trama do tricô, listras, sandálias), mesma modelo, pose igual ao esqueleto do frame 0.
**Nenhum workflow alterado.**

## 2026-11-21 — #9 W5 qualidade v1 (quadro + vídeo em alta, num workflow só)
**Criado (novo, nada existente foi alterado):**
- `WF/motion_W5_qualidade_v1.json`
- `PROJ/2 - files/workflows/build_W5.py` (gerador) e `W5_qualidade_v1_api.json` (cópia API)
- `D:\Comfy-Desktop\ComfyUI-Installs\cfui01\ComfyUI\user\default\motion_api\W5_qualidade_v1_api.json` (cópia API usada só para carregar no front)

**Estrutura:**
| Grupo | O que faz | Config. de qualidade (vs. teste) |
|---|---|---|
| Comum | nome `regata-rosa_look-02_q1`, pastas, produto `IN/motion/W2/produtos/regata-rosa_frente.png` | — |
| Etapa 1 (= W2 em alta) | produto + esqueleto `IN/motion/W2/look-02/pose-1.png` → FLUX.2 klein 9B base → primeiro quadro | **704×1248** (era 480×848) · **28 passos** (era 20) · produto **2 MP** (era 1) · esqueleto 0.9 MP (era 0.5) · só 1 ramo (pose do frame 0) · descrição vazia |
| Etapa 2 (= W3a em alta) | H3 ref2va + Fun ControlNet pose (`IN/motion/W3a/look-02_pose.mp4`) → vídeo | **704×1248** (era 480×864) · **turbo OFF = 20 passos** (era 4) · `ref_image_size` **max** (era match) · primeiro quadro ligado direto na saída da Etapa 1 (antes vinha de arquivo) |

Mantidos iguais: prompts (W2 corrigido e W3a), ControlNet strength 1.0, 124 frames, 24 fps, seed 20261121 fixa, res_multistep, BasicGuider (guidance 1.0).

**Por que 704×1248 e não 720×1280:** o nó `MiniMaxH3ReferenceToVideo` exige largura/altura múltiplas de 32; 720 não é.
**Saída:** `OUT/motion/W5_v1/<nome>/frame0_*.png` e `video_*.mp4`.
**Como rodar:** Ctrl+B no "Salva video (ETAPA 2)" → Run (só o quadro) → aprovar → reativar → Run (quadro vem do cache, só gera o vídeo).
**Status:** montado, não executado.

## 2026-11-21 — #8 W4 comparativo lado a lado (script, não workflow)
**Criado:** `PROJ/2 - files/workflows/W4_lado_a_lado.py`
- Uso: `python -I -X utf8 W4_lado_a_lado.py <original.mp4> <pose.mp4> <gerado.mp4> <saida.mp4>`
- Altura comum 864 px, rótulos ORIGINAL | ESQUELETO | GERADO, alinhamento por amostragem uniforme (mesma lógica do `VideoFrameSample` do W3a), áudio do gerado.
- **Gerado:** `OUT/motion/W4/regata-rosa_look-02_lado-a-lado.mp4` (1476×904, 124 frames, 24 fps, com áudio).

## 2026-11-21 — #7 W3a animação via H3 (teste)
**Criado:**
- `WF/motion_W3a_anima-h3.json`
- `PROJ/2 - files/workflows/build_W3a.py` e `W3a_api.json`
- `IN/motion/W3a/look-02_pose.mp4` (cópia de `OUT/motion/catalogo/_teste_B4-P13/pose_00001_.mp4`)
- `IN/motion/W3a/regata-rosa_look-02_frame0.png` (cópia de `OUT/motion/W2/look-02/pose-1_00004_.png`)

**Config.:** base no template `video_minimax_h3_fun_controlnet_union` sem o extrator SDPose interno (já é o W1). H3 ref2va + ControlNet strength 1.0; ref 1 = produto; primeiro quadro (`MiniMaxH3AddGuide` frame 0) = saída do W2; control = pose.mp4 reamostrado 150→124 frames (`VideoFrameSample` uniform); 480×864; turbo LoRA 4 passos via switch; `ref_image_size` match; seed fixa.
**Execução:** 1ª tentativa falhou no `VAEDecode` (IndexError em `comfy/model_management.py` `free_memory` — bug de gerenciamento de memória do ComfyUI 0.46.2, não do workflow). 2ª tentativa OK → `OUT/motion/W3a/regata-rosa_look-02/video_00001_.mp4`. Plano B se repetir: trocar por VAE Decode (Tiled).

## 2026-11-21 — #6 Vídeo de referência baixado
**Criado:** `PROJ/3 - Assets/referencias de pose/pozze_black-friday_DfEy39VA9dX.mp4` (Instagram @pozze.com.br, post DfEy39VA9dX; 720×1280, 30 fps, 11,1 s, com áudio, 2,25 MB).
Observações: tem giro de costas (bom teste de movimento); enquadramento corta no meio da coxa.
Já passou pelo W1 (pelo usuário), mas com o nome antigo → `OUT/motion/catalogo/_teste_B4-P13/pose_00002_.mp4` e `original_00002_.mp4` (330 frames).

## 2026-11-21 — #5 W2 corrigido (descrição da peça)
**Problema:** com produto novo (regata rosa), a roupa gerada veio do texto antigo do campo "Descricao da peca" (look-02: polo creme/saia ferrugem). **Texto da descrição vence a imagem 1.**
**Alterado (antes da regra de versionamento — arquivo sobrescrito):**
- `WF/motion_W2_pose-em-imagem.json`:
  - nó *Descricao da peca* → valor vazio; título "Descricao da peca (opcional, ingles, igual a imagem 1)"
  - nó *Prompt completo* `string_a` → + "The clothing must be copied only from image 1 … Do not invent or replace any clothing." ; `delimiter` → "\n\nOutfit details, exactly as in image 1: "
  - nó *Image 1 - Produto* → `motion/W2/produtos/regata-rosa_frente.png`
  - nó *Nome do teste* → `regata-rosa_look-02`
  - nota "Como usar" atualizada
- `PROJ/2 - files/workflows/build_W2.py` e `W2_api.json` regenerados com o mesmo.
**Criado:** `IN/motion/W2/produtos/regata-rosa_frente.png` (cópia de `IN/image (1).png`, enviada pelo usuário).
**Resultado:** com descrição vazia funcionou — roupa da imagem 1 na pose do esqueleto (`OUT/motion/W2/look-02/pose-*_00004_.png`).
**Versão anterior (v0, perdida no ComfyUI):** descrição = "cream short-sleeve knit polo with black-tipped collar and sleeve cuffs, rust satin midi slip skirt with ivory lace hem, brown leather slide sandals, woven straw tote bag"; delimiter "\n\nOutfit: "; prompt sem a frase "copied only from image 1"; produto `motion/W2/look-02/produto_provisorio_look-02.png`; nome `look-02`.

## 2026-11-21 — #4 W2 pose em imagem (teste)
**Criado:**
- `WF/motion_W2_pose-em-imagem.json`
- `PROJ/2 - files/workflows/build_W2.py` e `W2_api.json`
- `IN/motion/W2/look-02/pose-1..4.png` (keyframes de pose do W1) e `produto_provisorio_look-02.png` (frame 1 do original)

**Config.:** estrutura dos workflows `*_klein9b-base` do usuário: FLUX.2 klein 9B base fp8 + qwen_3_8b + full_encoder_small_decoder; image 1 = produto (1 MP), image 2 = esqueleto (0.5 MP) via ReferenceLatent; 4 ramos (um por keyframe); 480×848; 20 passos; CFG 3.5; seed 20261121 fixa (control "fixed").
**Execução 1:** OK, roupa fiel, mas poses parecidas demais com o produto para avaliar aderência.

## 2026-11-21 — #3 W1 primeiro teste
Rodado pelo usuário com `fashion-lookbook-look-02-video.mp4` (724×1268, 30 fps, 150 frames). Sem erro, ~38 s. Pose 576×1024, esqueletos completos (corpo, mãos, rosto, pés). Saiu em `OUT/motion/catalogo/_teste_B4-P13/` porque o campo "Nome do movimento" não foi trocado.

## 2026-11-21 — #2 Projeto migrado para esta pasta
- Pasta oficial passou de `E:\dev\Image Studio\motion` para `PROJ/` (a antiga ficou intacta).
- **Criado:** `PROJ/CLAUDE.md` (briefing completo, carregado automaticamente) e `PROJ/2 - files/workflows/W1_api.json` (cópia do antigo).

## Antes de 2026-11-21 — #1 W1 extração de pose (outro projeto)
`WF/motion_W1_extrai-pose.json`: LoadVideo → VideoTemporalCrop → SDPose (1024 + grid 32 px) → `OUT/motion/catalogo/<nome>/` pose/original mp4 + 4 keyframes de cada.
