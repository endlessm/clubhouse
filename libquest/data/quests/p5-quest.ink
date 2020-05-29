INCLUDE common.ink
# main character: estelle

VAR code = ""

-> begin

=== begin ===
-> p5_1

=== p5_1 ===
# character: estelle
- Hey {get_user_name()}, I've got something <b>super</b> cool for you! I've been learning a new programming language for making interactive art  called <b>p5.js</b> - The "js" part comes from <b>JavaScript</b> - you've probably heard of that before, it's a programming language used to run lots of websites.
+ [attracting: ❯] ❯
-> p5_2

=== p5_2 ===
# character: estelle
- In this activity, the <b>p5.js</b> code is on the far left, and the result of that code is in the middle. As you type, the code will constantly try to run, and update the middle area.
# character: estelle
- It's <b>super</b> important that you type any code <b>exactly</b> as we show it to you! Computers can be very picky about things like spaces! If you make any mistakes, you can always use Undo (<b>Ctrl + Z</b>), or if it's really bad, reset the code completely with the <b>Reload</b> button in the upper right.
+ [❯] ❯
-> p5_3

=== p5_3 ===
# character: estelle
- Let's start off with something simple - How about we change that background color. Find the line that says <tt>background(20);</tt>, and change it to read <tt>background('green');</tt>.
# character: estelle
- Dont forget the semicolon ( <b>;</b> ) at the end of the line, and pay attention to your spaces!
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "background('green');")]
+ [(wait for: code contains "background('Green');")]
+ [(wait for: code contains "background('GREEN');")]
-
(Done)
- -> p5_4

=== p5_4 ===
# character: estelle
- Great job! <b>p5.js</b> understands a lot of different color words - You could also use <tt>coral</tt>, <tt>lime</tt> or <tt>midnightblue</tt>, for example.
+ [❯] ❯
-> p5_5

=== p5_5 ===
# character: estelle
- Now, let's go a little deeper and change something about how the wave works! Find the line that says <tt>num = 20;</tt>, and change <b>20</b> to <b>5</b>. Don't forget to type the code exactly as you see it!
+ [(wait for: code contains "num = 5;")] (Done)
-> p5_6

=== p5_6 ===
# character: estelle
- Huh, where did all our lines go? Try changing <tt>num</tt> to <b>15</b>.
+ [(wait for: code contains "num = 15;")] (Done)
-> p5_7


=== p5_7 ===
# character: estelle
- That's a nice number! Next, let's change the space between the arcs. Try changing <tt>step</tt> to 30.
+ [(wait for: code contains "step = 30;")] (Done)
-> p5_8

=== p5_8 ===
# character: estelle
- Hmm, looks like we're going to need a bigger window to contain this wave! We can make the <b>canvas</b> (that's the name of the area the program draws things in) larger by changing the line that says <tt>createCanvas(400, 400)</tt>. Those two numbers control the width and height of your canvas, so let's make that a little bigger - increase the wdith to <b>600</b>.
+ [(wait for: code contains "createCanvas(600, 400);")] (Done)
-> p5_10


=== p5_10 ===
# character: estelle
- That looks better! You can keep changing the size, if you like.
# character: estelle
- Now, let's change the thickness of the arcs. Change <tt>strokeWeight</tt> from <b>5</b> to <b>10</b>.
+ [(wait for: code contains "strokeWeight(10);")] (Done)
-> p5_11


=== p5_11 ===
# character: estelle
- Nice! You can drop the <tt>strokeWeight</tt> back down, or change it to another number you like better.
# character: estelle
- Let's move on to some fun with colors - look for the line that says <tt>arcColor = 255</tt>.
# character: estelle
- That <b>variable</b> controls the color of all the lines in the wave - let's change it to <b>100</b>, and see what happens!
+ [(wait for: code contains "arcColor = 100;")] (Done)
-> p5_14


=== p5_14 ===
# character: estelle
- Now your wave is gray! If you want the wave to be blue, green or some other color, we need a more complex way of talking about colors. True, you can use color words, like you did for the background, but you can also describe colors in terms of the amounts of red, green, and blue they have.
# character: estelle
- For example, let's make the wave red - change the line with <b>arcColor</b> on it to <tt>arcColor = color(255, 0, 0);</tt>. Don't forget to double-check your spacing!
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "arcColor = color(255, 0, 0);")]
+ [(wait for: code contains "arcColor = color(255,0, 0);")]
+ [(wait for: code contains "arcColor = color(255, 0,0);")]
+ [(wait for: code contains "arcColor = color(255,0,0);")]
-
(Done)
- -> p5_16


=== p5_16 ===
# character: estelle
- See how the arcs are red? Change the color to <tt>(0, 255, 0);</tt> to give us some lucky green waves.
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "arcColor = color(0, 255, 0);")]
+ [(wait for: code contains "arcColor = color(0,255, 0);")]
+ [(wait for: code contains "arcColor = color(0, 255,0);")]
+ [(wait for: code contains "arcColor = color(0,255,0);")]
-
(Done)
- -> p5_18


=== p5_18 ===
# character: estelle
- Now let’s try blending our RGB values: <tt>color(0, 255, 255);</tt>
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "arcColor = color(0, 255, 255);")]
+ [(wait for: code contains "arcColor = color(0,255, 255);")]
+ [(wait for: code contains "arcColor = color(0, 255,255);")]
+ [(wait for: code contains "arcColor = color(0,255,255);")]
-
(Done)
- -> p5_19


=== p5_19 ===
# character: estelle
- Looks like green and blue make a lovely teal color! Let's try a more complex color - I love the purple you get with <tt>color(150, 0, 255)</tt>
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "arcColor = color(150, 0, 255);")]
+ [(wait for: code contains "arcColor = color(150,0, 255);")]
+ [(wait for: code contains "arcColor = color(150, 0,255);")]
+ [(wait for: code contains "arcColor = color(150,0,255);")]
-
(Done)
- -> p5_20


=== p5_20 ===
# character: estelle
- Great job! Now <b>those</b> are some beautiful waves.
# character: estelle
- We're at a crossroads: You can stay here and keep playing around with the colors and what we've learned so far, or... we can forge ahead into something more complicated. How does that sound?
* [👍] Let's keep moving!
-> p5_21
* [👎] I'm going to stay here and keep experimenting!
-> p5_stay


=== p5_stay ===
# character: estelle
- Have fun! Remember, you can always restart this quest if you change your mind.
-> END


=== p5_21 ===
# character: estelle
- OK, let's get complex. We'll make the arcs change color only when you click (or touch, if you're using a tablet) that part of the sceeen.
# character: estelle
- First, surround your existing <tt>doArcs(...</tt> code with <tt>if (mouseIsPressed) \{</tt>, and <tt>\}</tt>
# character: estelle
- Remember to be very careful of your spacing! Your code should look like this:
{snippet_p5_21()}
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "if (mouseIsPressed) \{ doArcs(arcColor); \}")]
+ [(wait for: code contains "if(mouseIsPressed)\{ doArcs(arcColor); \}")]
+ [(wait for: code contains "if (mouseIsPressed) \{doArcs(arcColor);\}")]
+ [(wait for: code contains "if(mouseIsPressed)\{doArcs(arcColor);\}")]
+ [(wait for: code contains "if ( mouseIsPressed ) \{ doArcs(arcColor); \}")]
-
(Done)
- -> p5_22


=== function snippet_p5_21 ===
# language: javascript
if (mouseIsPressed) \{ doArcs(arcColor); \}


=== p5_22 ===
# character: estelle
- Great, one last bit: create a new line after the one you just typed, and type <tt>else \{ doArcs(128); \}</tt>
# character: estelle
- If you're having trouble, carefully check that everything you've typed is in the correct place, with the correct spacing. Your code should look like this:
{snippet_p5_22()}
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "else \{ doArcs(128); \}")]
+ [(wait for: code contains "else\{ doArcs(128); \}")]
+ [(wait for: code contains "else\{doArcs(128);\}")]
+ [(wait for: code contains "else \{doArcs(128);\}")]
-
(Done)
- -> p5_23


=== function snippet_p5_22 ===
# language: javascript
if (mouseIsPressed) \{ doArcs(arcColor); \}
else \{ doArcs(128); \}


=== p5_23 ===
# character: estelle
- Great job, and we can also apply the same idea to the background color!
# character: estelle
- On the line with <tt>doArcs(...</tt>, add <tt>background(255);</tt> just before for <tt>doArcs(...</tt>
# character: estelle
- Your code should now look like this:
{snippet_p5_23()}
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "if (mouseIsPressed) \{ background(255); ")]
+ [(wait for: code contains "if(mouseIsPressed)\{ background(255); ")]
+ [(wait for: code contains "if(mouseIsPressed)\{background(255);")]
+ [(wait for: code contains "if (mouseIsPressed) \{background(255);")]
-
(Done)
- -> p5_24


=== function snippet_p5_23 ===
# language: javascript
if (mouseIsPressed) \{ background(255); doArcs(arcColor); \}
else \{ doArcs(128); \}


=== p5_24 ===
# character: estelle
- Do you see what we've done here? We used an <b>if</b> statement to change the behavior of this program depending on what you, the user, is doing!
# character: estelle
- If you click or touch the canvas, <tt>mouseIsPressed</tt> is <b>True</b>, so the if statement jumps to the first bit of code, and displays the arcs as your chosen color.
# character: estelle
- If you aren't clicking on or touching the canvas, <tt>mouseIsPressed</tt> is <b>False</b>, so it runs the code inside the <b>else</b> section, and the arcs are the other color.
# character: estelle
- You can think of <b>if</b> statements like they're a sentence - <i>If this test is true, do one thing, or else, do a different thing.</i>
+ [❯] ❯
-> p5_25


=== p5_25 ===
# character: estelle
- Finally, we’re going to introduce you to another power-user command: the <b>map</b> function. <b>Functions</b> take in some data, and output other data. <b>map</b> takes one set of numbers, and squishes or stretches it to fit another range of numbers. In this case, we're going to use <tt>map()</tt> to make the position of your mouse control the speed of the wave animation.
+ [❯] ❯
-> p5_26


=== p5_26 ===
# character: estelle
- First, let's get familiar with the numbers we'll be changing. Do you see the last line of our code, <tt>theta += 0.0523;</tt>? That number controls the speed of the wave.
# character: estelle
- <b>0.0523</b> is an awfully small number! Let's try increasing it to <tt>0.1</tt>. Remember to watch your spaces!
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "theta += 0.1;")]
+ [(wait for: code contains "theta +=0.1;")]
+ [(wait for: code contains "theta+=0.1;")]
-
(Done)
- -> p5_27


=== p5_27 ===
# character: estelle
- Wow, that's fast! What happens if we go much smaller than the original, say, <tt>0.001</tt>?
+ [(wait for: code contains "theta += 0.001;")] (Done)
-> p5_28

=== p5_28 ===
# character: estelle
- Very slow! Try to find a happy medium, or you can reset it to <tt>0.0523</tt>.
+ [❯] ❯
-> p5_29

=== p5_29 ===
# character: estelle
- Now, let’s use the map function to automate the things we did in the past few instructions. We'll make the vertical position of your cursor control the speed of the wave!
# character: estelle
- Change the number after <tt>theta +=</tt> to <tt>map(mouseY, height, 0, 0.001, 0.1);</tt> As usual, be careful to make sure your spaces and the numbers you're typing are correct.
TODO: Replace brute-force checks when we have a better check:
+ [(wait for: code contains "theta += map(mouseY, height, 0, 0.001, 0.1);")]
+ [(wait for: code contains "theta += map(mouseY,height,0,0.001,0.1);")]
+ [(wait for: code contains "theta+=map(mouseY, height, 0, 0.001, 0.1);")]
+ [(wait for: code contains "theta+=map(mouseY,height,0,0.001,0.1);")]
-
(Done)
- -> p5_30


=== p5_30 ===
# character: estelle
- Check it out! As you move your cursor higher, the wave speeds up. As you move it down, it slows down! And of course, you can still click or touch to change the colors.
+ [❯] ❯
-> p5_31


=== p5_31 ===
# character: estelle
- We're done for the moment, but there's so much to explore in <b>p5.js</b>! Feel free to change any of the variables you’ve learned, and play around as much as you like. If you'd like to keep going with more activities like this, I've got a whole set available in Hack for Endless OS!
# character: estelle
-You can learn how to use complex shapes, random numbers, programming tools like variables and loops, and even "paint" with sound or create your own games. I'd love to see you there!
->END
