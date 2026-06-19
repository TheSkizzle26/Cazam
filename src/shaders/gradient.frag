#version 330 core

/* OKLAB STUFF */

vec3 saturate(vec3 v) {
    return clamp(v, 0, 1);
}

// Weights: https://en.wikipedia.org/wiki/SRGB
vec3 LRGBtoXYZ(vec3 c) {
  mat3 rgb_to_xyz = mat3(
      0.4124, 0.3576, 0.1805,
      0.2126, 0.7152, 0.0722,
      0.0193, 0.1192, 0.9505);
  return saturate(rgb_to_xyz * c);
}

// Weights: https://en.wikipedia.org/wiki/SRGB
vec3 XYZtoLRGB(vec3 c) {
  mat3 xyz_to_rgb = mat3(
      3.24062548, -1.53720797, -0.4986286,
      -0.96893071,  1.87575606,  0.04151752,
      0.05571012, -0.20402105,  1.05699594);
  return saturate(xyz_to_rgb * c);
}

// Source: https://bottosson.github.io/posts/oklab/
vec3 XYZtoOKLAB(vec3 c) {
  mat3 m1 = mat3(
      0.8189330101, 0.3618667424, -0.1288597137,
      0.0329845436, 0.9293118715, 0.0361456387,
      0.0482003018, 0.2643662691, 0.6338517070);
  mat3 m2 = mat3(
      0.2104542553, 0.7936177850, -0.0040720468,
      1.9779984951, -2.4285922050, 0.4505937099,
      0.0259040371, 0.7827717662, -0.8086757660);
  c = m1 * c;
  c = pow(c, vec3(0.33333333333));
  return m2 * c;
}

// Source: https://bottosson.github.io/posts/oklab/
vec3 OKLABtoXYZ(vec3 c) {
  mat3 m1i = mat3(
       1.22701385, -0.55779998,  0.28125615,
      -0.04058018,  1.11225687, -0.07167668,
      -0.07638128, -0.42148198,  1.58616322);
  mat3 m2i = mat3(
      1.00000000,  0.39633779,  0.21580376,
      1.00000001, -0.10556134, -0.06385417,
      1.00000005, -0.08948418, -1.29148554);
  c = m2i * c;
  c = pow(c, vec3(3));
  return m1i * c;
}

// Source: https://bottosson.github.io/posts/oklab/
vec3 OKLABtoOKLCH(vec3 c) {
  float c_ = length(c.yz);
  float h_ = atan(c.z / c.y);
  return vec3(c.x, c_, h_);
}

// Source: https://bottosson.github.io/posts/oklab/
// Note: hue must be in units of radians.
vec3 OKLCHtoOKLAB(vec3 c) {
  float a = c.y * cos(c.z);
  float b = c.y * sin(c.z);
  return vec3(c.x, a, b);
}

vec3 LRGBtoOKLAB(vec3 c) {
  return XYZtoOKLAB(LRGBtoXYZ(c));
}

vec3 OKLABtoLRGB(vec3 c) {
  return XYZtoLRGB(OKLABtoXYZ(c));
}

vec3 LRGBtoOKLCH(vec3 c) {
  return OKLABtoOKLCH(XYZtoOKLAB(LRGBtoXYZ(c)));
}

vec3 OKLCHtoLRGB(vec3 c) {
  return XYZtoLRGB(OKLABtoXYZ(OKLCHtoOKLAB(c)));
}

/* OKLAB STUFF END */

in vec2 fragTexCoord;
out vec4 f_color;

const int numColors = 3;
uniform vec3 colors[numColors];
uniform uint screenWidth = 1920u;
uniform float aspectRatio;
uniform float noiseAmount;


// https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83
float mod289(float x){return x - floor(x * (1.0 / 289.0)) * 289.0;}
vec4 mod289(vec4 x){return x - floor(x * (1.0 / 289.0)) * 289.0;}
vec4 perm(vec4 x){return mod289(((x * 34.0) + 1.0) * x);}

// https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83
float noise(vec3 p){
    vec3 a = floor(p);
    vec3 d = p - a;
    d = d * d * (3.0 - 2.0 * d);

    vec4 b = a.xxyy + vec4(0.0, 1.0, 0.0, 1.0);
    vec4 k1 = perm(b.xyxy);
    vec4 k2 = perm(k1.xyxy + b.zzww);

    vec4 c = k2 + a.zzzz;
    vec4 k3 = perm(c);
    vec4 k4 = perm(c + 1.0);

    vec4 o1 = fract(k3 * (1.0 / 41.0));
    vec4 o2 = fract(k4 * (1.0 / 41.0));

    vec4 o3 = o2 * d.z + o1 * (1.0 - d.z);
    vec2 o4 = o3.yw * d.x + o3.xz * (1.0 - d.x);

    return o4.y * d.y + o4.x * (1.0 - d.y);
}

// https://stackoverflow.com/questions/23319289/is-there-a-good-glsl-hash-function
uint triple32(uint x)
{
    x ^= x >> 17;
    x *= 0xed5ad4bbU;
    x ^= x >> 11;
    x *= 0xac4c1b51U;
    x ^= x >> 15;
    x *= 0x31848babU;
    x ^= x >> 14;
    return x;
}


void main() {
    vec2 uv = fragTexCoord * vec2(aspectRatio, 1.0);

    float t = noise(vec3(uv.xy * 0.5 + vec2(0, 0.1), 1));
    t = (sin((t - 0.5) * 3.14159) + 1.0) * 0.5;
    t = smoothstep(0, 1, t);

    float scaled = t * float(numColors - 1);

    int a_idx = int(scaled);
    int b_idx = a_idx + 1;

    float sub_t = fract(scaled);
    sub_t = smoothstep(0, 1, sub_t);

    vec3 mixed = mix(
        LRGBtoOKLAB(colors[a_idx]),
        LRGBtoOKLAB(colors[b_idx]),
        sub_t
    );
    vec3 color = OKLABtoLRGB(mixed);

    // add white noise
    uint white_noise = triple32(uint(gl_FragCoord.y) * uint(screenWidth) + uint(gl_FragCoord.x));
    color += vec3(
            float(white_noise) / pow(2.0, 32.0)
    ) * noiseAmount;

    f_color = vec4(color, 1);
}