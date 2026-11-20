// Shared motion vocabulary (inlined by tools/build.py). All functions only add tweens at given times.
function titleIn(tl, sel, t, subAt) {
  tl.fromTo(sel + " .rule", { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, t);
  tl.fromTo(sel + " .ktxt", { opacity: 0, x: -16 }, { opacity: 1, x: 0, duration: 0.8, ease: "expo.out" }, t + 0.05);
  tl.fromTo(sel + " .w", { opacity: 0, filter: "blur(14px)", scale: 1.07 },
    { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.95, ease: "expo.out", stagger: 0.1 }, t + 0.1);
  if (document.querySelector(sel + " .sub")) tl.fromTo(sel + " .sub", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out" }, subAt === undefined ? t + 0.45 : subAt);
}
function blurOut(tl, sel, t, d) {
  tl.to(sel, { opacity: 0, filter: "blur(10px)", duration: d || 0.24, ease: "power2.in" }, t);
}
function placIn(tl, sel, t) {
  tl.fromTo(sel, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.7, ease: "power3.inOut" }, t);
  tl.fromTo(sel + " .frame", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.out" }, t + 0.45);
  tl.fromTo(sel + " .pk, " + sel + " .pb", { opacity: 0, filter: "blur(8px)" },
    { opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power3.out", stagger: 0.12 }, t + 0.35);
}
function printIn(tl, sel, t, rise) {
  tl.fromTo(sel, { opacity: 0, y: rise || 70 }, { opacity: 1, y: 0, duration: 0.9, ease: "expo.out" }, t);
  tl.fromTo(sel + " img", { scale: 1.14 }, { scale: 1, duration: 1.4, ease: "power3.out" }, t);
  tl.fromTo(sel + " .flash", { opacity: 0.85 }, { opacity: 0, duration: 0.35, ease: "power2.out" }, t + 0.02);
}
