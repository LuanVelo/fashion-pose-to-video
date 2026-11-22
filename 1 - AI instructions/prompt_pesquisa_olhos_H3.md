Preciso de uma pesquisa técnica (fóruns, GitHub issues, Reddit r/StableDiffusion e r/comfyui, Discord do ComfyUI, docs) sobre um problema de rosto/olhos em vídeo gerado com transferência de pose. Procure relatos de quem já passou por isso e soluções que funcionaram.

## Contexto
- ComfyUI 0.46 (só nós nativos, sem custom nodes), RTX 4090 24 GB.
- Pipeline: foto de produto (modelo vestindo a roupa) → FLUX.2 klein 9B gera o 1º quadro na pose → vídeo com **MiniMax H3 ref2va** (`MiniMaxH3ReferenceToVideo` + `MiniMaxH3AddGuide` no frame 0) + **MiniMax H3 Fun ControlNet union** (`MiniMaxH3FunControlNetApply`, strength 1.0, start 0 / end 1) recebendo um vídeo de esqueleto.
- Esqueleto extraído do vídeo de referência com **SDPose wholebody** (`SDPoseDrawKeypoints`): corpo + mãos + pés + cabeça (nariz, olhos, orelhas), sem os 68 pontos de rosto.
- Vídeo 896×1600, 124 frames, 24 fps, 20 passos, res_multistep, guidance 1.0. Rosto ocupa ~110 px de largura; olho ~20 px.

## Problema
Os olhos às vezes ficam no lugar errado ou vesgos ao longo do vídeo. A roupa fica fiel.

## O que já descobri
- Sobrepondo o esqueleto ao vídeo ORIGINAL, os pontos de olhos/nariz encaixam perfeitamente. No vídeo GERADO o rosto fica mais baixo e maior: os pontos dos "olhos" caem nas sobrancelhas e o "nariz" entre os olhos. Ou seja, a pessoa gerada tem proporção de cabeça diferente da pessoa do vídeo de referência, e o ControlNet puxa os olhos para a posição errada.
- Tirar os pontos de rosto (68 landmarks): não mudou nada.
- Tirar a cabeça inteira do esqueleto (`draw_head=False`): DESASTRE — o ControlNet union passou a ler o boneco como mapa de linhas e desenhou as linhas do esqueleto na roupa (costuras, mangas).
- Subir a resolução para 1088×1920: rosto bom, mas a roupa foi trocada e levou 59 min.
- Upscale do vídeo (RelayVSR x2) não corrige: amplia os defeitos.

## Perguntas
1. Esse desalinhamento entre a cabeça do esqueleto e o rosto gerado (diferença de proporção entre pessoas) é um problema conhecido em pose-transfer (Wan Animate, UniAnimate, MimicMotion, Animate Anyone, H3, ControlNet de pose em vídeo)? Como costumam resolver? Ex.: "pose retargeting", normalizar/realinhar o esqueleto ao corpo da pessoa gerada.
2. Reduzir strength ou end_percent do ControlNet (ex. parar em 50% dos passos) costuma resolver olho/rosto sem perder o movimento?
3. Existe forma de ajustar/reposicionar os pontos da cabeça do esqueleto (ou escalar o esqueleto) dentro do ComfyUI com nós nativos?
4. Técnicas de "face fix" em vídeo que funcionem com nós nativos do ComfyUI (ex.: segunda passada só no rosto com máscara, inpainting temporal, referência de rosto em close).
5. Alguém relatou o ControlNet union confundindo esqueleto incompleto com canny/lineart?

Responda em português, com links das fontes, separando o que é comprovado por relatos do que é suposição. Priorize soluções que rodem local no ComfyUI.
