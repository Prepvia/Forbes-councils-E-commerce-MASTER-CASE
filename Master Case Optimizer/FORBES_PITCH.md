# Forbes Council E-Commerce — Master Case Optimizer

Hey everyone,

I wanted to share something I built for us — something I wish I’d had years ago when I was guessing which box to use and losing money on every shipment.

---

## Why this actually matters

Most of us just pick a master case that “looks right” or stick with whatever we’ve always used. But the wrong box is expensive. Too big and you’re paying for air, worse pallet fit, and higher freight. Too small and you’re drowning in boxes, labels, and labor. And when your quantity doesn’t fit neatly? You’re either short or stuck with leftover units you didn’t plan for.

Nobody sits down with a ruler and the whole ULINE catalog. So we guess. And that guess costs us real money — every single shipment.

That’s why I built this. So we can stop guessing and see, in seconds, which box actually makes sense for our product and our volume.

---

## What it does (in plain English)

You enter your product: dimensions and weight. The tool looks at **every** standard ULINE box and scores them on what really matters: pallet fit, how full the box actually is, cost per unit, and how manageable it is to handle. You get a clear ranking and a 3D view of how your product packs inside.

Two ways to use it:

- **“I sell this all the time — what’s the best box?”**  
  That’s Unlimited mode. You get the top options, scores, and you can compare box price, cost per unit, and total estimated cost (including labels, handling, labor, and FBA inbound if you turn on the advanced options).

- **“I need to ship exactly X units.”**  
  That’s Limited mode. You can go Case Packed (one box type, zero waste — every unit fits) or Single Units (mix up to 3 box types so you hit your number exactly with no leftovers). Either way, you see total spend and per-unit cost so you know what you’re really paying.

So instead of “which box do we use?” you get “here are the best options, and here’s what each one costs us.”

---

## Why you should use it

Because your time is worth more than flipping through a catalog. Because a few cents per unit adds up fast when you’re moving volume. And because the right box means better pallet utilization, fewer touches, and less waste — which matters whether you’re sending to FBA, a 3PL, or retail.

I built it for the Forbes Council e-commerce community. It’s free, it runs on your machine (no data sent anywhere), and it uses the same ULINE boxes you can actually order. The costs in the tool are based on ULINE list pricing — we all know that can be negotiated with volume, but it’s a solid starting point.

---

## How to run it

1. Download the project folder (Master Case Optimizer).
2. Run `START_OPTIMIZER.bat` (or `python optimizer_engine.py`).
3. Open `http://localhost:8002` in your browser.
4. Enter your product, hit optimize, and you’re done.

If you use the advanced options, you can add label cost, handling per box (e.g. 25¢), labor (hourly rate and boxes per hour), and FBA inbound placement — so the total you see is much closer to what you’ll really spend.

---

Hope this helps. If you try it and have ideas to make it better, I’m all ears.

— Bernard  
(WAZIN · Forbes Council E-Commerce)
