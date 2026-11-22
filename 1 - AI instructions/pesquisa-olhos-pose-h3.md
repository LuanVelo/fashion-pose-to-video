# Pesquisa: olhos/rosto errados em vídeo com transferência de pose (MiniMax H3 + Fun ControlNet)

Data da pesquisa: 2026-11-22
Escopo: ComfyUI 0.46, **somente nós nativos**, RTX 4090 24 GB, execução local.

---

## 1. Contexto do pipeline

- Foto de produto (modelo vestindo a roupa) → **FLUX.2 klein 9B** gera o quadro 0 já na pose.
- Vídeo: **MiniMaxH3ReferenceToVideo** (ref2va) + **MiniMaxH3AddGuide** no frame 0 + **MiniMaxH3FunControlNetApply** (strength 1.0, start 0, end 1) recebendo o vídeo de esqueleto.
- Esqueleto: SDPose wholebody → **SDPoseDrawKeypoints** com corpo, mãos, pés e cabeça (nariz, olhos, orelhas), sem os 68 pontos de rosto.
- 896×1600, 124 frames, 24 fps, 20 passos, `res_multistep`, guidance 1.0.
- Rosto com ~110 px de largura e olho com ~20 px.

## 2. Sintoma e diagnóstico

**Sintoma:** os olhos às vezes ficam no lugar errado ou vesgos ao longo do vídeo. A roupa fica fiel.

**Testes já feitos:**

| Teste | Resultado |
|---|---|
| Esqueleto sobreposto ao vídeo ORIGINAL | Pontos de olhos e nariz encaixam perfeitamente |
| Esqueleto sobreposto ao vídeo GERADO | Rosto mais baixo e maior: os "olhos" caem nas sobrancelhas e o "nariz" entre os olhos |
| Remover os 68 landmarks de rosto | Sem mudança |
| `draw_head=False` | **Desastre**: o ControlNet leu o boneco como mapa de linhas e desenhou as linhas na roupa (costuras, mangas) |
| Gerar em 1088×1920 | Rosto bom, mas a roupa foi trocada e levou 59 min |
| Upscale RelayVSR x2 | Amplia os defeitos |

**Diagnóstico:** a pessoa gerada (vinda do FLUX) tem proporção de cabeça diferente da pessoa do vídeo de referência. O ControlNet puxa os olhos para a posição dos pontos do esqueleto, e o ref2va/AddGuide puxa para o rosto real do quadro 0. Esse conflito provavelmente causa o olho errado ou vesgo intermitente. O desalinhamento já existe no frame 0.

---

## 3. Achados da pesquisa

Legenda: **[COMPROVADO]** = documentação ou relato público. **[SUPOSIÇÃO]** = inferência ainda não validada.

### 3.1 O desalinhamento de proporção é um problema conhecido **[COMPROVADO]**

- Artigo do Wan-Animate: como personagem e vídeo de referência têm proporções ósseas e tamanhos diferentes, eles fazem **pose retargeting** nos esqueletos extraídos do vídeo de referência.
  https://arxiv.org/pdf/2509.14055
- Artigo One-to-All Animation: os métodos atuais (UniAnimate-DiT, Wan-Animate, MimicMotion, StableAnimator) exigem pares referência–pose alinhados. Quando o retargeting falha, a identidade deriva. A correção deles substitui aleatoriamente as estruturas faciais das poses no treino, para **desacoplar identidade e esqueleto**. Ou seja, os pontos de rosto carregam a geometria facial da pessoa de origem.
  https://arxiv.org/html/2511.22940v2
- Issue no GitHub do Kijai (Wan Animate): "o sistema acaba tentando esticar a personagem para caber no esqueleto". Contorno sugerido: desligar partes do esqueleto, com perda de fidelidade de movimento.
  https://github.com/kijai/ComfyUI-WanVideoWrapper/issues/1262
- O retargeting do Kijai (custom) escala a cabeça pelo fator global do corpo. Não tem correção própria de cabeça/rosto.
  https://deepwiki.com/kijai/ComfyUI-WanAnimatePreprocess/4.5-pose-retargeting-system
- O nó custom "Pose Detection OneToAll Animation" reajusta o esqueleto às proporções da referência, membro a membro (usar só como referência de método).
  https://comfy.icu/node/PoseDetectionOneToAllAnimation

### 3.2 Strength / end_percent do ControlNet

- **[COMPROVADO]** A doc oficial do H3 Fun ControlNet só diz para manter guidance 1.0 e subir o strength acima de 1 apenas se a saída se afastar do controle. Não fala de start/end.
  https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fun-controlnet
- **[COMPROVADO]** No VideoX-Fun, `control_context_scale` escala cada skip de controle: 1.0 é o mais forte, 0.0 desliga.
  https://comfyui-wiki.com/en/news/2026-08-24-minimax-h3-fun-controlnet-union
- **[COMPROVADO]** Para o Z-Image Fun Union (mesma equipe), a faixa ótima indicada é 0.65–0.80.
  https://huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union
- **[COMPROVADO]** Em imagem, pose ControlNet com strength 1.0 e end_percent 0.5 é uma configuração comum.
  https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/discussions/50
- **[SUPOSIÇÃO]** Não há relato em vídeo H3 de que isso conserte os olhos. Hipótese: os passos iniciais fixam layout e movimento, e os finais fazem o detalhe do rosto. Então end 0.6–0.7 pode soltar o rosto sem perder o movimento. Risco: a roupa ou a silhueta derivarem um pouco.

### 3.3 Edição do esqueleto com nós nativos

- **[COMPROVADO]** Em `SDPoseDrawKeypoints`, `draw_body` e `draw_head` são independentes. Com `draw_head=False` + `draw_body=True`, sai o corpo sem cabeça. Com `draw_body=False` + `draw_head=True`, saem **só a cabeça e o ponto do pescoço**. Entradas: draw_body, draw_hands, draw_face, draw_feet, stick_width, face_point_size, score_threshold, draw_head.
  https://docs.comfy.org/built-in-nodes/SDPoseDrawKeypoints
- **[COMPROVADO]** Não existe nó nativo para editar `POSE_KEYPOINT`.
- **[SUPOSIÇÃO]** É possível fazer o retargeting por camadas de imagem (ver plano, passo B).

### 3.4 Face fix em vídeo

- **[COMPROVADO]** O Fun ControlNet Union tem **inpainting nativo**: com uma máscara na entrada `mask`, as regiões marcadas com 1 são regeneradas sob controle do `source_video` opcional, e o resto do quadro fica fixo.
  https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fun-controlnet
- **[COMPROVADO]** Discussão no HF: o H3 distorce rostos pequenos (quanto menor o rosto no quadro, pior). Planos fechados e médios ficam bons. ~1.0 MP é citado como ponto ideal com o LoRA turbo. Sugestões dadas: recortar a região, re-renderizar e mesclar com máscara suavizada; denoise ~0.15 v2v para casos leves; regenerar em resolução maior em vez de usar upscaler latente.
  https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/30
- **[COMPROVADO]** O ComfyUI-H3-FaceRefine (custom) implementa exatamente o face detailer para H3. Parâmetros úteis para copiar:
  - crop = 2.5× a altura do rosto (rosto em ~40% do crop), canvas de 512 a 768;
  - centro do crop suavizado numa janela gaussiana de 21 frames e tamanho em 51 frames (evita o crop "respirar");
  - denoise por frame: 1.0 para rostos ≤30 px, 0.35 para ≥120 px;
  - colagem com máscara de feather 4–8.
  https://github.com/Carasibana/ComfyUI-H3-FaceRefine

### 3.5 ControlNet union confundindo esqueleto incompleto com lineart

- **[COMPROVADO]** O Union usa um único checkpoint para Canny/Depth/HED/MLSD/Pose (e mais tipos na v2.0), sem seletor de tipo.
- **[COMPROVADO]** A v2.0 (22/09/2026) adiciona Scribble, Layout e Gray e dobra os blocos de injeção. Para usar, basta trocar o patch no ModelPatchLoader.
  https://comfyui-wiki.com/en/news/2026-09-22-minimax-h3-fun-controlnet-union-2
- **[SUPOSIÇÃO]** Não foi achado relato direto. Inferência: o modelo deduz o tipo pela aparência; sem cabeça, o boneco parece MLSD/Canny (linhas finas em fundo preto), o que explica as costuras desenhadas na roupa. **Nunca remover a cabeça do esqueleto.**

---

## 4. Plano de ação (ordem de teste)

Regras para todos os testes: seed fixa e clip curto (~8–10 s ou menos) para comparar. Variar uma coisa por vez.

### A. Afrouxar o ControlNet (barato)

Matriz sugerida no `MiniMaxH3FunControlNetApply`:

| strength | end_percent |
|---|---|
| 1.0 | 0.7 |
| 1.0 | 0.6 |
| 0.8 | 1.0 |
| 0.8 | 0.7 |

Avaliar três coisas: olhos (posição/vesgo), fidelidade da roupa e fidelidade do movimento.
Conferir também se o patch é o Union v1 ou o v2.0.

### B. Retargeting manual da cabeça por camadas (só nós nativos)

1. Rodar o SDPose no **quadro 0 do FLUX** e no **frame 0 do vídeo de referência**.
2. Medir nos dois: pescoço→nariz, distância entre os olhos e posição do nariz. Calcular `escala = d_flux / d_ref` e o deslocamento (dx, dy).
   - Observação: os nós nativos não leem keypoints numericamente. Medir uma vez à mão (sobrepor e medir em pixels) ou num script externo. A transformação é constante para o vídeo todo.
3. Camada A: `SDPoseDrawKeypoints` com `draw_head=False` (corpo, mãos e pés).
4. Camada B: `SDPoseDrawKeypoints` com `draw_body=False, draw_head=True` (cabeça + pescoço).
5. Transformar B: `ImageScaleBy` (escala) + `ImageCrop`/padding para pivotar no pescoço + deslocamento (dx, dy).
6. Máscara de B: `ImageToMask` → `ThresholdMask`.
7. `ImageCompositeMasked` de B sobre A (x, y = deslocamento). Esse é o novo `control_video`.
8. Validar sobrepondo o novo esqueleto ao quadro 0 do FLUX: os pontos dos olhos devem cair nos olhos.

Limitação: a correção é fixa e não acompanha giros fortes da cabeça. A linha do pescoço pode ficar levemente quebrada, o que deve ser aceitável.

### C. Segunda passada só no rosto (inpaint nativo do H3)

1. Definir um **crop fixo** (`ImageCrop`) que cubra a trajetória da cabeça em todos os frames (~330×330 px, cerca de 3× a largura do rosto).
2. Ampliar o crop para ~768×768 (`ImageScale`, lanczos). Assim o rosto vai de ~110 px para ~250 px.
3. Rodar o H3 + Fun ControlNet em modo inpaint:
   - `source_video` = o crop ampliado;
   - `mask` = oval do rosto com feather (sem cobrir o cabelo/pescoço para não mexer no resto);
   - referência = close do rosto recortado do quadro 0 do FLUX;
   - controle de pose recortado e ampliado com a mesma transformação, ou nenhum. Testar os dois.
4. Reduzir para o tamanho original e colar com `ImageCompositeMasked` + máscara suavizada.
5. Se a cabeça se mover muito, o crop fixo não serve. Nesse caso seria preciso um crop com tracking, como no H3-FaceRefine (custom node), ou dividir o vídeo em trechos.

### D. Fallback

- Gerar a 1088×1920 só se A a C falharem (59 min e troca de roupa).
- Não usar upscale (VSR ou latente) como correção de rosto.

---

## 5. Critérios de sucesso

- Olhos estáveis, sem vesgo, nos 124 frames.
- Roupa fiel à foto do produto (cor, costuras e modelagem).
- Movimento fiel ao vídeo de referência.
- Tempo de render próximo do atual (896×1600).
