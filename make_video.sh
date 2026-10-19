#!/usr/bin/env bash
set -e
OUT=/home/arielp/Work/hackathon-bli
FONT=/usr/share/fonts/liberation/LiberationSans-Bold.ttf
FONTREG=/usr/share/fonts/liberation/LiberationSans-Regular.ttf
BG=0x0f172a
W=1280; H=720

# 1. Title (8s)
ffmpeg -y -f lavfi -i "color=c=${BG}:s=${W}x${H}:d=8" -vf \
 "drawtext=fontfile=${FONT}:text='RegTech AI Compliance Agent':fontcolor=white:fontsize=52:x=(w-text_w)/2:y=(h-text_h)/2-40,drawtext=fontfile=${FONTREG}:text='AI compliance for smart contracts and RWA tokens':fontcolor=#a5b4fc:fontsize=26:x=(w-text_w)/2:y=(h-text_h)/2+30,drawtext=fontfile=${FONTREG}:text='BLI Legal Tech Hackathon 2 - LegalTech and RegTech':fontcolor=#64748b:fontsize=18:x=(w-text_w)/2:y=h-60" \
 -c:v libx264 -pix_fmt yuv420p -r 30 "$OUT/seg1.mp4" 2>/dev/null

# 2. Problem (10s)
ffmpeg -y -f lavfi -i "color=c=${BG}:s=${W}x${H}:d=10" -vf \
 "drawtext=fontfile=${FONT}:text='The Problem':fontcolor=#f87171:fontsize=40:x=(w-text_w)/2:y=80,drawtext=fontfile=${FONTREG}:text='Smart contracts ship without compliance review':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=200,drawtext=fontfile=${FONTREG}:text='Legal teams cannot read Solidity':fontcolor=#cbd5e1:fontsize=20:x=(w-text_w)/2:y=260,drawtext=fontfile=${FONTREG}:text='Auditors do not check sanctions or KYC':fontcolor=#cbd5e1:fontsize=20:x=(w-text_w)/2:y=300,drawtext=fontfile=${FONTREG}:text='Unilateral minting  upgradeable proxies  sanctioned addresses':fontcolor=#cbd5e1:fontsize=20:x=(w-text_w)/2:y=340,drawtext=fontfile=${FONTREG}:text='Discovered only after launch':fontcolor=#f87171:fontsize=20:x=(w-text_w)/2:y=380" \
 -c:v libx264 -pix_fmt yuv420p -r 30 "$OUT/seg2.mp4" 2>/dev/null

# 3. Solution (10s)
ffmpeg -y -f lavfi -i "color=c=${BG}:s=${W}x${H}:d=10" -vf \
 "drawtext=fontfile=${FONT}:text='The Solution':fontcolor=#818cf8:fontsize=40:x=(w-text_w)/2:y=80,drawtext=fontfile=${FONTREG}:text='Paste a contract  pick a jurisdiction':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=200,drawtext=fontfile=${FONTREG}:text='Get a risk score  sanctions hits  KYC/AML posture':fontcolor=#cbd5e1:fontsize=20:x=(w-text_w)/2:y=260,drawtext=fontfile=${FONTREG}:text='and a legal-document attestation report in seconds':fontcolor=#cbd5e1:fontsize=20:x=(w-text_w)/2:y=300,drawtext=fontfile=${FONTREG}:text='Jurisdictions US - EU - Singapore - UAE':fontcolor=#a5b4fc:fontsize=20:x=(w-text_w)/2:y=360" \
 -c:v libx264 -pix_fmt yuv420p -r 30 "$OUT/seg3.mp4" 2>/dev/null

# 4. Demo risky (20s) - screenshot
ffmpeg -y -loop 1 -i /home/arielp/demo_risky.png -f lavfi -i anullsrc -t 20 -vf \
 "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:${BG},drawtext=fontfile=${FONT}:text='Demo Risky Contract':fontcolor=#f87171:fontsize=28:x=40:y=20" \
 -c:v libx264 -pix_fmt yuv420p -r 30 -shortest "$OUT/seg4.mp4" 2>/dev/null

# 5. Demo clean (20s) - screenshot
ffmpeg -y -loop 1 -i /home/arielp/demo_clean.png -f lavfi -i anullsrc -t 20 -vf \
 "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:${BG},drawtext=fontfile=${FONT}:text='Demo Clean Contract':fontcolor=#34d399:fontsize=28:x=40:y=20" \
 -c:v libx264 -pix_fmt yuv420p -r 30 -shortest "$OUT/seg5.mp4" 2>/dev/null

# 6. Jurisdictions (12s)
ffmpeg -y -f lavfi -i "color=c=${BG}:s=${W}x${H}:d=12" -vf \
 "drawtext=fontfile=${FONT}:text='4 Jurisdictions':fontcolor=#818cf8:fontsize=40:x=(w-text_w)/2:y=80,drawtext=fontfile=${FONTREG}:text='US SEC/FinCEN  GENIUS Act':fontcolor=#cbd5e1:fontsize=22:x=(w-text_w)/2:y=200,drawtext=fontfile=${FONTREG}:text='EU MiCA  EMT/ART stablecoins':fontcolor=#cbd5e1:fontsize=22:x=(w-text_w)/2:y=240,drawtext=fontfile=${FONTREG}:text='Singapore MAS AML/CFT':fontcolor=#cbd5e1:fontsize=22:x=(w-text_w)/2:y=280,drawtext=fontfile=${FONTREG}:text='UAE VARA/SCA rulebook':fontcolor=#cbd5e1:fontsize=22:x=(w-text_w)/2:y=320" \
 -c:v libx264 -pix_fmt yuv420p -r 30 "$OUT/seg6.mp4" 2>/dev/null

# 7. Closing (10s)
ffmpeg -y -f lavfi -i "color=c=${BG}:s=${W}x${H}:d=10" -vf \
 "drawtext=fontfile=${FONT}:text='RegTech AI Compliance Agent':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=120,drawtext=fontfile=${FONTREG}:text='Open source - stdlib Python + single-page frontend':fontcolor=#a5b4fc:fontsize=20:x=(w-text_w)/2:y=200,drawtext=fontfile=${FONTREG}:text='github.com/Arielpoghon/regtech-compliance-agent':fontcolor=#64748b:fontsize=18:x=(w-text_w)/2:y=260,drawtext=fontfile=${FONTREG}:text='BLI Legal Tech Hackathon 2':fontcolor=#64748b:fontsize=16:x=(w-text_w)/2:y=h-60" \
 -c:v libx264 -pix_fmt yuv420p -r 30 "$OUT/seg7.mp4" 2>/dev/null

# Concat
cat > "$OUT/concat.txt" <<EOF
file '$OUT/seg1.mp4'
file '$OUT/seg2.mp4'
file '$OUT/seg3.mp4'
file '$OUT/seg4.mp4'
file '$OUT/seg5.mp4'
file '$OUT/seg6.mp4'
file '$OUT/seg7.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i "$OUT/concat.txt" -c copy "$OUT/demo.mp4" 2>/dev/null

echo "=== DONE ==="
ls -lh "$OUT/demo.mp4"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT/demo.mp4"
