import React from 'react';

class QuestCard extends React.Component {
  render() {
    const backClass = `background ${this.props.quest.id}`;
    return (
      <div className="QuestCard" onClick={this.props.onClick}>
        <div className={backClass}>
        </div>
        <div className="info">
            <div className={this.props.quest.dificulty}></div>
            <p>{this.props.quest.name}</p>
        </div>
      </div>
    );
  }
}

class Pathway extends React.Component {
  openQuest(q) {
    this.props.app.openQuest(q);
  }

  render() {
    const quests = [
        {
          name: 'HTML - Using Colors',
          dificulty: 'easy',
          id: 'htmlintro2',
          url: 'https://codepen.io/madetohack/pen/BaaKggj?editors=1000#code-area',
        }
    ];

    const className = "animation ada Character";
    return (
      <div className="Pathway">
        <div className={className} />
        <div className="quests">
            { quests.map(q =>
                <QuestCard quest={q} onClick={this.openQuest.bind(this, q)} />
            )}
        </div>
      </div>
    );
  }
}

export default Pathway;
