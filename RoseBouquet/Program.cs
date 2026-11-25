// ============================================================================
//  «Букет розовых французских роз с красными лилиями» — анимированное видео.
//
//  Сценарий (15 секунд, 30 fps, вертикальный кадр 720x1280):
//    0.0 – 6.0 с   букет медленно «дышит» и покачивается;
//    6.0 – 9.5 с   камера плавно приближается к одной из красных лилий;
//    9.5 – 12.0 с  в центре лилии появляется красное сердце и бьётся;
//    12.0 – 13.5 с сердце растворяется, рассыпаясь на маленькие сердечки;
//    13.5 – 15.0 с остаётся надпись "I love you".
//
//  Зависимости: SkiaSharp (+ NativeAssets.Linux) — кроссплатформенный рендер.
//
//  Запуск:
//      dotnet run -c Release                 // кадры -> ./frames/f0000.png ...
//      ffmpeg -y -framerate 30 -i frames/f%04d.png -pix_fmt yuv420p -crf 18 out.mp4
// ============================================================================
using SkiaSharp;

string outDir = args.Length > 0 ? args[0] : "frames";
Directory.CreateDirectory(outDir);

const int W = 720, H = 1280, FPS = 30;
const double DUR = 15.0;
int total = (int)(DUR * FPS);

static double ZoomAt(double t)
{
    if (t < 6.0) return 1.0;
    if (t >= 9.5) return 5.0;
    double u = Math.Clamp((t - 6.0) / 3.5, 0, 1);
    u = u * u * (3.0 - 2.0 * u);              // smoothstep
    return 1.0 + 4.0 * u;
}

var focusLily = new SKPoint(360f, 470f);      // та самая красная лилия (координаты холста)

for (int fi = 0; fi < total; fi++)
{
    double t = fi / (double)FPS;
    using var surface = SKSurface.Create(new SKImageInfo(W, H, SKColorType.Rgba8888));
    Scene.RenderFrame(surface.Canvas, t, W, H, focusLily, ZoomAt(t));
    using var img = surface.Snapshot();
    using var data = img.Encode(SKEncodedImageFormat.Png, 100);
    using var fs = File.Create(Path.Combine(outDir, $"f{fi:D4}.png"));
    data.SaveTo(fs);
    if (fi % 30 == 0) Console.WriteLine($"frame {fi}/{total}");
}
Console.WriteLine("done");

// ===========================================================================
static class Scene
{
    public record Rose(float X, float Y, float Size, int Seed, float HueShift);
    public record Lily(float X, float Y, float Size, float TiltDeg, int Seed);

    public static readonly List<Rose> Roses = new();
    public static readonly List<Lily> Lilies = new();
    public static readonly List<SKPoint> Sparks = new();

    static readonly SKTypeface SerifFace =
        SKTypeface.FromFile("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf");

    static Scene()
    {
        var rng = new Random(11);
        (float, float, float)[] roseSpots =
        {
            (215, 330, 62), (300, 268, 70), (392, 258, 66), (472, 300, 60),
            (250, 420, 68), (352, 372, 76), (455, 402, 64), (540, 355, 55),
            (185, 470, 52), (300, 500, 62), (420, 492, 58), (512, 462, 52),
            (355, 200, 50), (255, 210, 46), (455, 212, 46), (200, 385, 44),
            (560, 420, 42),
        };
        foreach (var (x, y, s) in roseSpots)
            Roses.Add(new Rose(x, y, s, rng.Next(100000), (float)(rng.NextDouble() * 24 - 12)));

        (float, float, float, float)[] lilySpots =
        {
            (150, 262, 62, -32), (566, 268, 60, 34),
            (118, 540, 50, -52), (600, 520, 52, 48),
            (360, 470, 74, 3),               // <- фокусная лилия
        };
        foreach (var (x, y, s, tl) in lilySpots)
            Lilies.Add(new Lily(x, y, s, tl, rng.Next(100000)));

        var r2 = new Random(7);
        for (int i = 0; i < 26; i++)
            Sparks.Add(new SKPoint((float)(W * r2.NextDouble()), (float)(H * 0.9 * r2.NextDouble())));
    }

    // ---------------- helpers ----------------
    static double Smooth(double x) { x = Math.Clamp(x, 0, 1); return x * x * (3 - 2 * x); }

    static SKColor Mix(SKColor a, SKColor b, double k)
    {
        k = Math.Clamp(k, 0, 1);
        return new SKColor(
            (byte)(a.Red + (b.Red - a.Red) * k),
            (byte)(a.Green + (b.Green - a.Green) * k),
            (byte)(a.Blue + (b.Blue - a.Blue) * k));
    }

    static SKColor WithA(SKColor c, double alpha) =>
        c.WithAlpha((byte)Math.Clamp(alpha * 255, 0, 255));

    // спираль Фибоначчи для лепестков розы
    static IEnumerable<(float dx, float dy, float sz, float rotDeg)> PetalLayout(int seed, float size)
    {
        var rng = new Random(seed);
        double ga = Math.PI * (3 - Math.Sqrt(5));
        for (int i = 0; i < 26; i++)
        {
            float r = size * (float)Math.Sqrt((i + 0.6) / 26.0) * 0.62f;
            float a = (float)(i * ga + rng.NextDouble() * 0.35);
            float sz = size * (0.30f + 0.42f * (1 - i / 26f)) * (float)(0.85 + rng.NextDouble() * 0.3);
            yield return ((float)(Math.Cos(a) * r), (float)(Math.Sin(a) * r), sz, a * 57.29578f);
        }
    }

    static SKPath RoundedPetal(float w, float h)
    {
        // лепесток-«лодочка»: центр сверху (w/2, 0), низ (w/2, h)
        var p = new SKPath();
        p.MoveTo(w / 2, 0);
        p.CubicTo(w * 0.92f, 0, w * 1.12f, h * 0.55f, w / 2, h);
        p.CubicTo(-w * 0.12f, h * 0.55f, w * 0.08f, 0, w / 2, 0);
        p.Close();
        return p;
    }

    static SKPath LilyPetal(float w, float len)
    {
        // вытянутый острый лепесток лилии: основание (w/2, len), кончик (w/2, 0)
        var p = new SKPath();
        p.MoveTo(w / 2, len);
        p.CubicTo(-w * 0.18f, len * 0.62f, w * 0.06f, len * 0.12f, w / 2, 0);
        p.CubicTo(w * 0.94f, len * 0.12f, w * 1.18f, len * 0.62f, w / 2, len);
        p.Close();
        return p;
    }

    static SKPath HeartPath(float cx, float cy, float s)
    {
        float top = cy - s * 0.55f;
        var p = new SKPath();
        p.MoveTo(cx, cy + s * 0.75f);
        p.CubicTo(cx - s * 1.15f, cy + s * 0.05f, cx - s * 0.62f, top - s * 0.28f, cx - s * 0.02f, top + s * 0.12f);
        p.CubicTo(cx + s * 0.02f, top + s * 0.12f, cx + s * 0.62f, top - s * 0.28f, cx + s * 1.15f, cy + s * 0.05f);
        p.CubicTo(cx + s * 0.62f, cy + s * 0.55f, cx + s * 0.2f, cy + s * 0.62f, cx, cy + s * 0.75f);
        p.Close();
        return p;
    }

    // двойной удар «lub-dub»
    static double Heartbeat(double phase)
    {
        double bump(double c, double w) => Math.Exp(-Math.Pow((phase - c) / w, 2));
        return 0.85 * bump(0.12, 0.06) + 0.55 * bump(0.30, 0.07);
    }

    // ---------------- фон ----------------
    static void DrawBackground(SKCanvas c, double t)
    {
        using var bg = SKShader.CreateLinearGradient(
            new SKPoint(0, 0), new SKPoint(0, H),
            new[] { new SKColor(28, 14, 22), new SKColor(8, 4, 10) }, null, SKShaderTileMode.Clamp);
        using var bgp = new SKPaint { Shader = bg };
        c.DrawRect(new SKRect(0, 0, W, H), bgp);

        // тёплое боке за букетом
        double pulse = 0.5 + 0.5 * Math.Sin(t * 0.8);
        var rng = new Random(9);
        for (int i = 0; i < 14; i++)
        {
            float rr = 40 + rng.Next(10, 90);
            float px = (float)(W * rng.NextDouble());
            float py = (float)(300 + 500 * rng.NextDouble() + Math.Sin(i * 2.4 + t * 0.15) * 12);
            byte a = (byte)(22 + pulse * 14);
            using var sh = SKShader.CreateRadialGradient(
                new SKPoint(px, py), rr,
                new[] { new SKColor(255, 170, 150, a), new SKColor(255, 170, 150, 0) },
                null, SKShaderTileMode.Clamp);
            using var paint = new SKPaint { Shader = sh };
            c.DrawCircle(px, py, rr, paint);
        }

        // виньетка
        using var vg = SKShader.CreateRadialGradient(
            new SKPoint(W / 2f, H / 2f), H * 0.62f,
            new[] { new SKColor(0, 0, 0, 0), new SKColor(0, 0, 0, 150) },
            new[] { 0.55f, 1f }, SKShaderTileMode.Clamp);
        using var vgp = new SKPaint { Shader = vg };
        c.DrawRect(new SKRect(0, 0, W, H), vgp);
    }

    // ---------------- роза ----------------
    static void DrawRose(SKCanvas c, Rose r)
    {
        var basePink = new SKColor((byte)Math.Clamp(236 + r.HueShift, 180, 255),
                                   (byte)Math.Clamp(120 - r.HueShift * 0.5, 70, 170), 150);
        var deepPink = new SKColor(170, 55, 92);
        var lightPink = new SKColor(255, 205, 220);

        foreach (var (dx, dy, sz, rotDeg) in PetalLayout(r.Seed, r.Size))
        {
            float depth = Math.Clamp(sz / r.Size, 0, 1);
            var edge = Mix(deepPink, Mix(basePink, lightPink, 0.35 + 0.5 * depth), depth);

            c.Save();
            c.Translate(r.X + dx - sz / 2, r.Y + dy - sz * 0.42f);
            c.RotateDegrees(rotDeg);

            using var path = RoundedPetal(sz, sz * 0.84f);
            using var sh = SKShader.CreateRadialGradient(
                new SKPoint(sz / 2, sz * 0.78f), sz * 0.95f,
                new[] { lightPink, Mix(lightPink, edge, 0.55), edge },
                new[] { 0f, 0.5f, 1f }, SKShaderTileMode.Clamp);
            using var paint = new SKPaint { Shader = sh, IsAntialias = true };
            c.DrawPath(path, paint);
            using var outline = new SKPaint
            {
                Color = new SKColor(120, 30, 60, 60),
                Style = SKPaintStyle.Stroke, StrokeWidth = 1.2f, IsAntialias = true,
            };
            c.DrawPath(path, outline);
            c.Restore();
        }

        using (var core = new SKPaint { Color = new SKColor(140, 45, 80), IsAntialias = true })
            c.DrawCircle(r.X, r.Y, r.Size * 0.10f, core);
    }

    // ---------------- лилия ----------------
    static void DrawLily(SKCanvas c, Lily l)
    {
        var rng = new Random(l.Seed);
        c.Save();
        c.Translate(l.X, l.Y);
        c.RotateDegrees(l.TiltDeg);

        float w = l.Size * 0.44f, len = l.Size * 1.0f;
        for (int i = 0; i < 6; i++)
        {
            c.Save();
            c.RotateDegrees(i * 60f + (float)(rng.NextDouble() * 10 - 5));
            c.Translate(-w / 2, -len);

            using var path = LilyPetal(w, len);
            using var sh = SKShader.CreateLinearGradient(
                new SKPoint(w / 2, len), new SKPoint(w / 2, 0),
                new[] { new SKColor(120, 10, 20), new SKColor(225, 45, 45), new SKColor(250, 120, 95) },
                new[] { 0f, 0.55f, 1f }, SKShaderTileMode.Clamp);
            using var paint = new SKPaint { Shader = sh, IsAntialias = true };
            c.DrawPath(path, paint);
            using var pen = new SKPaint
            {
                Color = new SKColor(90, 5, 15, 120),
                Style = SKPaintStyle.Stroke, StrokeWidth = 1.1f, IsAntialias = true,
            };
            c.DrawPath(path, pen);

            // жилка + крапинки
            using var vein = new SKPaint
            {
                Color = new SKColor(150, 25, 25, 150),
                Style = SKPaintStyle.Stroke, StrokeWidth = 1.4f, IsAntialias = true,
            };
            c.DrawLine(w / 2, len * 0.85f, w / 2, len * 0.05f, vein);
            using var dots = new SKPaint { Color = new SKColor(95, 10, 20, 200), IsAntialias = true };
            for (int d = 0; d < 7; d++)
            {
                float yy = len * (0.25f + 0.1f * d);
                float xx = w / 2 + (float)(rng.NextDouble() - 0.5) * w * 0.6f;
                c.DrawCircle(xx, yy, 2f, dots);
            }
            c.Restore();
        }

        // тычинки
        using (var stamen = new SKPaint
        {
            Color = new SKColor(250, 215, 120, 230),
            Style = SKPaintStyle.Stroke, StrokeWidth = 1.6f, IsAntialias = true,
        })
        using (var anther = new SKPaint { Color = new SKColor(190, 90, 20, 240), IsAntialias = true })
        {
            for (int i = 0; i < 5; i++)
            {
                double rad = (-40 + i * 20) * Math.PI / 180.0;
                float lx = (float)Math.Sin(rad) * l.Size * 0.55f;
                float ly = -(float)Math.Cos(rad) * l.Size * 0.75f;
                c.DrawLine(0, 0, lx, ly, stamen);
                c.DrawCircle(lx, ly, 3f, anther);
            }
        }
        c.Restore();
    }

    // ---------------- стебли / листья / обёртка ----------------
    static void DrawStems(SKCanvas c)
    {
        var rng = new Random(3);
        using var paint = new SKPaint
        {
            Color = new SKColor(30, 70, 36, 90),
            Style = SKPaintStyle.Stroke, StrokeWidth = 4f,
            StrokeCap = SKStrokeCap.Round, IsAntialias = true,
        };
        foreach (var r in Roses)
        {
            float sx = r.X + (float)(rng.NextDouble() * 30 - 15);
            using var path = new SKPath();
            path.MoveTo(r.X, r.Y + r.Size * 0.3f);
            path.QuadTo((r.X + sx) / 2, r.Y + 120, 360 + (r.X - 360) * 0.35f, 760);
            c.DrawPath(path, paint);
        }
    }

    static void DrawLeaves(SKCanvas c, double sway)
    {
        var leafDark = new SKColor(22, 62, 34);
        var leafLight = new SKColor(70, 130, 60);
        (float, float, float, float)[] spots =
        {
            (140, 620, 120, -52), (580, 610, 125, 52), (250, 660, 100, -23),
            (470, 655, 105, 26), (95, 430, 90, -69), (625, 430, 90, 69),
            (360, 690, 110, 3),
        };
        foreach (var (x, y, len, ang) in spots)
        {
            c.Save();
            c.Translate(x, y);
            c.RotateDegrees(ang + (float)sway * 8);

            using var p = new SKPath();
            p.MoveTo(0, 0);
            p.CubicTo(-len * 0.28f, -len * 0.45f, -len * 0.10f, -len * 0.9f, 0, -len);
            p.CubicTo(len * 0.10f, -len * 0.9f, len * 0.28f, -len * 0.45f, 0, 0);
            p.Close();
            using var sh = SKShader.CreateLinearGradient(
                new SKPoint(0, 0), new SKPoint(0, -len),
                new[] { leafDark, leafLight }, null, SKShaderTileMode.Clamp);
            using var paint = new SKPaint { Shader = sh, IsAntialias = true };
            c.DrawPath(p, paint);
            using var vein = new SKPaint
            {
                Color = new SKColor(15, 40, 20, 120),
                Style = SKPaintStyle.Stroke, StrokeWidth = 1.5f, IsAntialias = true,
            };
            c.DrawLine(0, 0, 0, -len, vein);
            c.Restore();
        }
    }

    static void DrawWrap(SKCanvas c)
    {
        using var p = new SKPath();
        p.MoveTo(150, 640);
        p.CubicTo(200, 800, 300, 900, 360, 1010);
        p.CubicTo(420, 900, 520, 800, 570, 640);
        p.CubicTo(480, 700, 240, 700, 150, 640);
        p.Close();
        using var sh = SKShader.CreateLinearGradient(
            new SKPoint(150, 640), new SKPoint(570, 1010),
            new[] { new SKColor(246, 226, 200), new SKColor(196, 150, 130) },
            null, SKShaderTileMode.Clamp);
        using var paint = new SKPaint { Shader = sh, IsAntialias = true };
        c.DrawPath(p, paint);
        using var fold = new SKPaint
        {
            Color = new SKColor(150, 100, 80, 60),
            Style = SKPaintStyle.Stroke, StrokeWidth = 2f, IsAntialias = true,
        };
        for (int i = 0; i < 4; i++)
        {
            float x = 220 + i * 80;
            using var fp = new SKPath();
            fp.MoveTo(x, 680);
            fp.CubicTo(x + 10, 800, x + 25, 880, 360, 990);
            c.DrawPath(fp, fold);
        }
    }

    // ---------------- сердце ----------------
    static void DrawHeart(SKCanvas c, double t)
    {
        if (t < 9.5) return;
        double appear = Smooth((t - 9.5) / 0.9);
        double vanish = t < 12.0 ? 0 : Smooth((t - 12.0) / 1.3);
        double alpha = appear * (1 - vanish);
        if (alpha <= 0.01) return;

        double ph = (t * 1.15) % 1.0;
        double beat = Heartbeat(ph);
        float s = 95f * (1 + (float)beat * 0.22f) * (float)(0.6 + 0.4 * appear);
        float cx = W / 2f, cy = H / 2f - 40;

        // свечение
        float glowR = s * 1.9f;
        using (var gs = SKShader.CreateRadialGradient(
                   new SKPoint(cx, cy), glowR,
                   new[] { WithA(new SKColor(255, 60, 80), 0.45 * alpha), new SKColor(255, 60, 80, 0) },
                   null, SKShaderTileMode.Clamp))
        using (var gp = new SKPaint { Shader = gs, IsAntialias = true })
            c.DrawCircle(cx, cy, glowR, gp);

        using var heart = HeartPath(cx, cy, s);
        using (var hs = SKShader.CreateRadialGradient(
                   new SKPoint(cx - s * 0.2f, cy - s * 0.25f), s * 1.6f,
                   new[] { WithA(new SKColor(255, 90, 110), alpha), WithA(new SKColor(170, 10, 35), alpha) },
                   null, SKShaderTileMode.Clamp))
        using (var hp = new SKPaint { Shader = hs, IsAntialias = true })
            c.DrawPath(heart, hp);

        using (var rim = new SKPaint
        {
            Color = WithA(new SKColor(255, 170, 180), 0.8 * alpha),
            Style = SKPaintStyle.Stroke, StrokeWidth = 3f, IsAntialias = true,
        })
            c.DrawPath(heart, rim);

        using (var hl = new SKPaint { Color = WithA(SKColors.White, 0.5 * alpha), IsAntialias = true })
            c.DrawOval(cx - s * 0.31f, cy - s * 0.35f, s * 0.22f, s * 0.14f, hl);
    }

    // ---------------- рассыпающиеся сердечки ----------------
    static void DrawPetalsBurst(SKCanvas c, double t)
    {
        if (t < 12.0) return;
        double u = (t - 12.0) / 1.5;
        var rng = new Random(42);
        using var paint = new SKPaint { Color = new SKColor(255, 90, 110), IsAntialias = true };
        for (int i = 0; i < 34; i++)
        {
            double ang = rng.NextDouble() * Math.PI * 2;
            double spd = 60 + rng.NextDouble() * 260;
            float x = (float)(W / 2 + Math.Cos(ang) * spd * u * 1.6);
            float y = (float)(H / 2 - 40 + Math.Sin(ang) * spd * u * 1.6 - 120 * u * u);
            float sz = (float)(10 + rng.NextDouble() * 14) * (float)(1 - u * 0.6);
            double a = (1 - Smooth(u)) * 0.86;
            if (a <= 0.02 || sz <= 1) continue;
            paint.Color = WithA(new SKColor(255, 90, 110), a);
            using var p = HeartPath(x, y, sz);
            c.DrawPath(p, paint);
        }
    }

    // ---------------- текст ----------------
    static void DrawText(SKCanvas c, double t)
    {
        if (t < 13.3) return;
        double u = Smooth((t - 13.3) / 1.2);
        string text = "I love you";
        using var typeface = SKTypeface.FromFamilyName("DejaVu Serif",
            SKFontStyleWeight.Bold, SKFontStyleWidth.Normal, SKFontStyleSlant.Italic);
        using var font = new SKFont(typeface ?? SerifFace, 64);
        float y = H / 2f - 40;

        float tw;
        using (var mfp = new SKPaint { Typeface = typeface ?? SerifFace, TextSize = 64 })
            tw = mfp.MeasureText(text);
        float tx = W / 2f - tw / 2f;

        using (var shadow = new SKPaint { Color = new SKColor(0, 0, 0, (byte)(160 * u)), IsAntialias = true })
            c.DrawText(text, tx + 4, y + 5, font, shadow);

        using (var ts = SKShader.CreateLinearGradient(
                   new SKPoint(tx, y - 60), new SKPoint(tx + tw, y + 20),
                   new[] { WithA(new SKColor(255, 235, 240), u), WithA(new SKColor(255, 120, 150), u) },
                   null, SKShaderTileMode.Clamp))
        using (var tp = new SKPaint { Shader = ts, IsAntialias = true })
            c.DrawText(text, tx, y, font, tp);

        double hu = Smooth((t - 14.0) / 0.8);
        if (hu > 0.01)
        {
            using var hp = HeartPath(W / 2f, y + 95, 22 * (float)hu);
            using var hb = new SKPaint { Color = WithA(new SKColor(255, 80, 100), hu), IsAntialias = true };
            c.DrawPath(hp, hb);
        }
    }

    // искорки
    static void DrawSparks(SKCanvas c, double t)
    {
        using var p = new SKPaint { Color = new SKColor(255, 220, 210), IsAntialias = true };
        foreach (var sp in Sparks)
        {
            double tw = 0.5 + 0.5 * Math.Sin(t * 2 + sp.X * 0.05 + sp.Y * 0.03);
            p.Color = new SKColor(255, 220, 210, (byte)(70 * tw));
            c.DrawCircle(sp.X, sp.Y, (float)(1.5 + 2 * tw), p);
        }
    }

    // ---------------- кадр ----------------
    public static void RenderFrame(SKCanvas c, double t, int w, int h, SKPoint focus, double zoom)
    {
        c.Clear(new SKColor(8, 4, 10));
        DrawBackground(c, t);

        double sway = Math.Sin(t * 0.9) * 0.02 + Math.Sin(t * 1.7) * 0.008;

        // ---- камера: плавный наезд на фокусную лилию ----
        c.Save();
        c.Translate(w / 2f, h / 2f - 60);
        c.Scale((float)zoom);
        c.Translate(-focus.X, -focus.Y);
        // лёгкое дыхание букета
        c.Translate(w / 2f, 500f);
        c.RotateDegrees((float)(sway * 57.3 * 0.3));
        c.Translate(-w / 2f, -500f);

        DrawWrap(c);
        DrawStems(c);
        DrawLeaves(c, sway);

        foreach (var r in Roses) DrawRose(c, r);
        foreach (var l in Lilies) DrawLily(c, l);

        c.Restore();

        DrawSparks(c, t);
        DrawHeart(c, t);
        DrawPetalsBurst(c, t);
        DrawText(c, t);

        // мягкая дымка при близком плане
        if (zoom > 1.5)
        {
            double haze = Math.Min(0.18, (zoom - 1.5) * 0.05);
            using var hb = new SKPaint { Color = WithA(new SKColor(40, 10, 20), haze) };
            c.DrawRect(new SKRect(0, 0, w, h), hb);
        }
    }

    public const int W = 720, H = 1280;
}
