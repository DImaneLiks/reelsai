# -*- coding: utf-8 -*-
"""Озвучка «А что если…» через F5-TTS (русская модель Misha24-10, голос клонируется с образца).

  ../../reels/F5-TTS-main/.venv/bin/python tts.py            # все реплики -> vo/NN.wav
  ../../reels/F5-TTS-main/.venv/bin/python tts.py 3 7        # только реплики 3 и 7
Ударения расставляет RUAccent; ручная правка — символ + перед ударной гласной в LINES_FIX.
"""
import os, sys, json
ROOT = os.path.dirname(os.path.abspath(__file__))
F5 = "/Users/dmitrijpostnov/Documents/reels/F5-TTS-main"
CKPT = os.path.join(F5, "ckpts/ru/F5TTS_v1_Base_v2/model_last_inference.safetensors")
VOCAB = os.path.join(F5, "ckpts/ru/F5TTS_v1_Base/vocab.txt")
REF = os.path.join(ROOT, "ref_alex.wav")
REF_TEXT = "В вагоне сорок человек. Все в сером. Все смотрят в пол. Но присмотрись. У одного из-под рукава торчит красная нитка. У второго. У десятого."
REF_TEXT_ACC = "В ваг+оне с+орок челов+ек. Вс+е в с+ером. Вс+е см+отрят в п+ол. Но присмотр+ись. У одног+о из-под рукав+а торч+ит кр+асная н+итка. У втор+ого. У дес+ятого."
LINES = json.load(open(os.path.join(ROOT, "lines.json")))
LINES_FIX = {
 1: "Он не стар+ел. И ег+о в+идели жив+ым — ч+ерез дес+ятки лет п+осле см+ерти.",
 2: "Одн+а граф+иня встр+етила ег+о в +юности — и ч+ерез полв+ека узн+ала: то же лиц+о, тот же в+озраст.",
 3: "Ег+о зв+али граф Сен-Жерм+ен — и отк+уда он вз+ялся, не знал никт+о.",
 4: "А на зв+аных +ужинах не ел ни кр+ошки. Шепт+али, что он пьёт эликс+ир бессм+ертия.",
 5: "О Клеоп+атре и Христ+е он расск+азывал так, б+удто в+идел их сам.",
 6: "В т+ысяча семьс+от в+осемьдесят четвёртом год+у граф +умер в Герм+ании.",
 7: "Но ч+ерез год ег+о +имя сто+ит в сп+иске гост+ей т+айного собр+ания мас+онов в Пар+иже.",
 8: "Заг+адка п+ервая: з+апись о похорон+ах есть — а мог+илы нет.",
 9: "Заг+адка втор+ая: Казан+ова в+идел, как он преврат+ил м+едную мон+ету в золот+ую.",
 10: "Заг+адка тр+етья: Наполе+он Тр+етий собр+ал о нём ц+елый арх+ив. В т+ысяча восемьс+от с+емьдесят п+ервом арх+ив сгор+ел.",
 11: "Мош+енник, алх+имик — +или челов+ек, кот+орый нашёл бессм+ертие? Пиш+ите в коммент+ариях.",
}
SEEDS = {}
OUT = os.path.join(ROOT, "vo"); os.makedirs(OUT, exist_ok=True)

def _patch_audio():
    """torchcodec без системного FFmpeg не грузится — читаем wav через soundfile."""
    os.environ["PATH"] = os.path.join(ROOT, "bin") + ":" + os.environ["PATH"]
    import torch, torchaudio, soundfile as sf
    def load(path, *a, **k):
        x, sr = sf.read(str(path), dtype="float32", always_2d=True)
        return torch.from_numpy(x.T.copy()), sr
    def save(path, wav, sr, *a, **k):
        sf.write(str(path), wav.detach().cpu().numpy().T, sr)
    torchaudio.load = load; torchaudio.save = save


PREPS = {"на", "за", "по", "до", "без", "из", "под", "над", "о", "об", "от", "у", "к", "с", "в", "со", "ко", "во", "при", "про"}
def clean_acc(t):
    """Служебные слова (предлоги) всегда без ударения."""
    out = []
    for w in t.split(" "):
        out.append(w.replace("+", "") if w.replace("+", "").strip("«»,.!?—").lower() in PREPS else w)
    return " ".join(out)

def safe_acc(acc, text):
    """RUAccent иногда падает на незнакомом слове — тогда идём по словам и оставляем его без ударения."""
    try:
        return acc.process_all(text)
    except Exception:
        out = []
        for w in text.split(" "):
            try: out.append(acc.process_all(w))
            except Exception: out.append(w)
        return " ".join(out)

def main():
    _patch_audio()
    only = [int(x) for x in sys.argv[1:]]
    from ruaccent import RUAccent
    acc = RUAccent(); acc.load(omograph_model_size="turbo3.1", use_dictionary=True, tiny_mode=False)
    from f5_tts.api import F5TTS
    tts = F5TTS(model="F5TTS_v1_Base", ckpt_file=CKPT, vocab_file=VOCAB, device="mps")
    ref_text = REF_TEXT_ACC
    for i, text in enumerate(LINES, 1):
        if only and i not in only: continue
        t = LINES_FIX.get(i) or clean_acc(safe_acc(acc, text))
        print(f"[{i:02d}] {t}", flush=True)
        tts.infer(REF, ref_text, t, file_wave=os.path.join(OUT, f"{i:02d}.wav"), nfe_step=32, seed=SEEDS.get(i, 7),
                  show_info=lambda *a: None, progress=None, remove_silence=False)

if __name__ == "__main__":
    main()
