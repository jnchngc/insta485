import React from 'react';
import PropTypes from 'prop-types';

class Likes extends React.Component {
  /* Display number of likes and like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      numLikes: 0,
      lognameLikesThis: 'false',
      url: '',
    };

    // lets us call this.updateDatabse in our html
    this.updateDatabase = this.updateDatabase.bind(this);
    this.updateLikesOnDoubleClick = this.updateLikesOnDoubleClick.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get number of likes
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          numLikes: data.likes_count,
          lognameLikesThis: data.logname_likes_this,
          url: data.url,
        });
      })
      .catch((error) => console.log(error));
  }

  updateDatabase() {
    const { lognameLikesThis, url, numLikes } = this.state;
    const prevNumLikes = numLikes;
    if (lognameLikesThis) {
      // call the delete api for likes
      fetch(url, {
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
        method: 'delete',
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(() => {
          this.setState({
            numLikes: prevNumLikes - 1,
            lognameLikesThis: 0,
          });
        })
        .catch((error) => console.log(error));
    } else {
      // call the post api for likes
      fetch(url, {
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        method: 'post',
        body: JSON.stringify({}),
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(() => {
          this.setState({
            numLikes: prevNumLikes + 1,
            lognameLikesThis: 1,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  updateLikesOnDoubleClick() {
    const { lognameLikesThis, url, numLikes } = this.state;
    const prevNumLikes = numLikes;
    if (!lognameLikesThis) {
      fetch(url, {
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
        method: 'post',
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(() => {
          this.setState({
            numLikes: prevNumLikes + 1,
            lognameLikesThis: 1,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  render() {
    // This line automatically assigns this.state.numLikes to the const variable numLikes
    const { numLikes } = this.state;
    const { lognameLikesThis } = this.state;

    // Render number of likes
    return (
      <div className="likes">
        <button className="like-unlike-button" type="button" onClick={this.updateDatabase}>
          {lognameLikesThis === 0 ? 'like' : 'unlike'}
        </button>
        <p>
          {numLikes}
          {' '}
          like
          {numLikes !== 1 ? 'sssssss' : ''}
        </p>
      </div>
    );
  }
}

Likes.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Likes;
