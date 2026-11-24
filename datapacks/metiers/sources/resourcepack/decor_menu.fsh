#version 330

// Décor des menus en jeu (Les Couillons, 24/11/2026) : remplace le flou du monde derrière les dialogues, le menu Échap
// et les options. Paysage de nuit en pixel art, animé : ciel dégradé, étoiles qui scintillent, lune, aurore, montagnes,
// colline de sapins, lucioles. Tout est calculé ici, sans texture. Passe « décor » de post_effect/blur.json.

#moj_import <minecraft:globals.glsl>

uniform sampler2D InSampler;

layout(std140) uniform SamplerInfo {
    vec2 OutSize;
    vec2 InSize;
};

in vec2 texCoord;

out vec4 fragColor;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float bruit(float x) {
    float i = floor(x);
    float f = fract(x);
    float a = hash(vec2(i, 3.7));
    float b = hash(vec2(i + 1.0, 3.7));
    return mix(a, b, f * f * (3.0 - 2.0 * f));
}

float fbm(float x) {
    return 0.55 * bruit(x) + 0.28 * bruit(x * 2.1 + 5.0) + 0.17 * bruit(x * 4.3 + 11.0);
}

void main() {
    // grille de pixels : 200 pixels de haut quelle que soit la fenêtre
    float lignes = 200.0;
    float asp = OutSize.x / max(OutSize.y, 1.0);
    vec2 grille = vec2(floor(lignes * asp), lignes);
    vec2 cel = floor(texCoord * grille);
    vec2 uv = (cel + 0.5) / grille;          // 0..1, y vers le haut
    float x = uv.x * asp;
    float y = uv.y;
    float t = GameTime * 1200.0;            // secondes environ (GameTime fait un tour en 20 minutes)

    // ciel : nuit profonde en haut, violet puis braise à l'horizon
    vec3 haut = vec3(0.035, 0.03, 0.09);
    vec3 milieu = vec3(0.13, 0.07, 0.22);
    vec3 horizon = vec3(0.42, 0.17, 0.20);
    vec3 col = mix(horizon, milieu, smoothstep(0.18, 0.45, y));
    col = mix(col, haut, smoothstep(0.45, 0.95, y));

    // étoiles (une sur 60 cellules), scintillement
    float h = hash(cel);
    if (h > 0.983 && y > 0.35) {
        float sc = 0.55 + 0.45 * sin(t * (1.5 + 3.0 * hash(cel + 7.0)) + h * 60.0);
        col += vec3(0.85, 0.85, 1.0) * sc * smoothstep(0.35, 0.6, y);
    }

    // aurore : rideau vert et turquoise qui ondule
    float ond = 0.70 + 0.05 * sin(x * 2.3 + t * 0.15) + 0.03 * sin(x * 5.7 - t * 0.23);
    float dist = abs(y - ond);
    float rideau = smoothstep(0.10, 0.0, dist) * (0.55 + 0.45 * sin(x * 37.0 + t * 0.6 + sin(x * 3.0) * 4.0));
    col += mix(vec3(0.10, 0.55, 0.35), vec3(0.15, 0.45, 0.65), 0.5 + 0.5 * sin(x * 1.7 + t * 0.1)) * rideau * 0.33;

    // lune et halo
    vec2 lune = vec2(0.80 * asp, 0.80);
    float dl = length(vec2(x, y) - lune);
    col += vec3(0.55, 0.45, 0.35) * smoothstep(0.25, 0.0, dl) * 0.18;
    if (dl < 0.065) {
        float cr = hash(floor((vec2(x, y) - lune) * 70.0));
        col = mix(vec3(0.93, 0.90, 0.78), vec3(0.75, 0.72, 0.62), step(0.8, cr));
    }

    // montagnes lointaines
    float m1 = 0.22 + 0.30 * pow(fbm(x * 2.6 + 2.0), 1.8) + 0.02 * bruit(x * 30.0);
    if (y < m1) {
        col = mix(vec3(0.045, 0.03, 0.08), vec3(0.10, 0.06, 0.15), smoothstep(m1 - 0.15, m1, y));
        if (y > m1 - 0.006) col = vec3(0.30, 0.18, 0.30);                                        // crête éclairée par la lune
    }

    // colline proche et sapins
    float m2 = 0.17 + 0.05 * sin(x * 2.0 + 1.3) + 0.03 * fbm(x * 5.0);
    float largeurSapin = 0.035;
    float idx = floor(x / largeurSapin);
    float fx = fract(x / largeurSapin) - 0.5;
    float hs = 0.05 + 0.07 * hash(vec2(idx, 9.1));
    float sapin = step(0.3, hash(vec2(idx, 2.2))) * step(y, m2 + hs * (1.0 - abs(fx) * 2.2)) * step(m2 - 0.01, y);
    if (y < m2 || sapin > 0.5) {
        col = vec3(0.025, 0.035, 0.05);
        // fenêtres d'un hameau, chaudes
        if (y < m2 - 0.02 && y > m2 - 0.05 && hash(vec2(idx, 5.5)) > 0.86 && abs(fx) < 0.12)
            col = vec3(1.0, 0.72, 0.30) * (0.8 + 0.2 * sin(t * 2.0 + idx));
    }

    // lucioles dorées qui montent doucement
    for (int i = 0; i < 14; i++) {
        float fi = float(i);
        float px = fract(hash(vec2(fi, 1.0)) + 0.01 * sin(t * 0.3 + fi)) * asp;
        float py = fract(hash(vec2(fi, 2.0)) + t * 0.012 * (0.5 + hash(vec2(fi, 3.0)))) * 0.5;
        vec2 d = (vec2(x, y) - vec2(px, py)) * grille.y;
        float l = 0.5 + 0.5 * sin(t * 3.0 + fi * 2.0);
        if (abs(d.x) < 0.6 && abs(d.y) < 0.6) col = mix(col, vec3(1.0, 0.85, 0.35), l);
        else col += vec3(1.0, 0.75, 0.3) * l * 0.25 * smoothstep(3.0, 0.0, length(d));
    }

    // vignette et une pointe du monde derrière, très sombre, pour garder la sensation d'être en jeu
    vec2 c = texCoord - 0.5;
    col *= 1.0 - 0.55 * dot(c, c) * 2.0;
    vec3 monde = texture(InSampler, texCoord).rgb;
    col = mix(col, monde * 0.35, 0.06);

    fragColor = vec4(col, 1.0);
}
