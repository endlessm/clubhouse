import React from 'react';
import { CSSTransitionGroup } from 'react-transition-group';

class Tome  extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      items: [],
      lastMessage: 0,
    };

    this.messages = [
        {id: 1, text: "Hey again! Ready to dive a little deeper, <b>{{user_name}}</b>?"},
        {id: 2, text: "First things first - let's get back to that web page previewer."},
        {id: 3, text: "If it's not opening, run or switch to your browser. You can hold <b>Alt</b> and press <b>Tab</b> to cycle through active programs, or look at the bottom of the screen."},
        {id: 4, text: 'You can also click this link: <u><span insert_hyphens="false" foreground="#3584E4">https://codepen.io/madetohack/pen/BaaKggj?editors=1000</span></u>'},
        {id: 5, text: "Here's a fun fact - Just based on our last lesson, you already know enough to make your own webpage!"},
        {id: 6, text: "If you did, though, all you'd have is boring black text on a white background. Let's spice that up a little!"},
        {id: 7, text: 'Find an opening <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;p&gt;</span></tt> tag in your code, and add <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">style=”color:blue”</span></tt> after the <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">p</span></tt>. It should look like this: <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;p style="color:blue"&gt;</span></tt>'},
        {id: 8, text: "Congratulations! You just <b>styled</b> some text! Now let's get even fancier."},
        {id: 9, text: 'Find another <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;p&gt;</span></tt> tag and make <b>that</b> text orange.'},
        {id: 10, text: 'If you did that right, the tag should look like this: <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;p style="color:orange"&gt;</span></tt>, and your text should be orange!'},
        {id: 11, text: 'I wonder what happens if you try the same thing with an <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;h1&gt;</span></tt> or <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;h2&gt;</span></tt> tag? Try making one of those purple.'},
        {id: 12, text: 'If you did it right, it should look something like <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;h1 style="color:purple"&gt;</span></tt>'},
        {id: 13, text: "Nice. What if you wanted to use a super-special shade of green, though? How would you do that?"},
        {id: 14, text: "It'd be really cool if we had a more specific way to express color, where we could say exactly how we want to mix it."},
        {id: 15, text: "You see where I'm going with this, right? We totally do have that! It's called <b>hex color</b>, and it lets you create colors by using 6-digit numbers."},
        {id: 16, text: '¡Here\'s an example hex color - <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">#76EECF</span></tt>'},
        {id: 17, text: 'To use this hex color in your webpage, replace one of your color words with that hex code: <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">#76EECF</span></tt>'},
        {id: 18, text: 'If you edited a <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;p&gt;</span></tt> tag, it would be <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;p style="color:#76EECF"&gt;</span></tt>'},
        {id: 19, text: 'Cool! Change the numbers around and see if you can create another color!'},
        {id: 20, text: "Hex color uses 1 - 9, and A B C D E F as numbers - It's a little out of our way right now to explain why, I can tell you later if you're interested."},
        {id: 21, text: 'If you want to use a color picker, you can try this webpage: <u><span insert_hyphens="false" foreground="#3584E4">https://htmlcolorcodes.com/</span></u>'},
        {id: 22, text: "Ok, so you've got some color chops now. But do you know what would <b>really</b> make this page look cool?"},
        {id: 23, text: 'I think we need to change the background color to something less boring. Look for the <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;body&gt;</span></tt> tag in the code.'},
        {id: 24, text: 'It should be near the top of the page. Inside that tag, put <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">style="background-color:coral"</span></tt>, just like you put the <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">color</span></tt> information into a <tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;p&gt;</span></tt> tag.'},
        {id: 25, text: 'Your body tag should look like this -<tt><span insert_hyphens="false" foreground="#287A8C" background="#FFFFFF">&lt;body style="background-color:coral"&gt;</span></tt>'},
        {id: 26, text: "Niiice! Now that's going to turn some heads."},
        {id: 27, text: "So, how does it feel to have the tools to paint the whole internet? Come find me back in the Clubhouse to keep going!"},
    ];

    this.addItem();
  }

  addItem() {
    let newItems = this.state.items;
    let lastMsg = this.state.lastMessage;
    let newMsg = this.messages[lastMsg++];
    newItems.push(newMsg);
    this.setState({items: newItems, lastMessage: lastMsg});

    // if (lastMsg < this.messages.length)
    //     setTimeout(() => { this.addItem(); }, 2000);
  }

  render() {
    const items = this.state.items.reverse().map((item) => (
      <div key={item.id} className="message riley">
        {item.text}
      </div>
    ));

    return (
      <div className="Tome" onClick={() => this.addItem()}>
        <CSSTransitionGroup
          transitionName="example"
          transitionEnterTimeout={500}
          transitionLeaveTimeout={300}>
          {items}
        </CSSTransitionGroup>
      </div>
    );
  }
}

class Quest extends React.Component {
  render() {
    const iframeStyles = {
      width: window.innerWidth - 480,
      height: window.innerHeight - 100,
    };

    return (
      <div className="Quest">
        <iframe src={this.props.quest.url} style={iframeStyles} title="iframe">
          <p>Your browser does not support iframes.</p>
        </iframe>
        <Tome quest={this.props.quest} />
      </div>
    );
  }
}

export default Quest;
