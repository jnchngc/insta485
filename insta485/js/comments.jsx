import React from 'react';
import PropTypes from 'prop-types';

class Comments extends React.Component {
  /* Display number of likes and like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    const { url } = this.props;
    const urlArg = url;
    this.state = {
      comments: [],
      url: urlArg,
      commentBox: '',
    };

    // lets us call this.updateDatabse in our html
    this.updateDatabase = this.updateDatabase.bind(this);
    this.handleChange = this.handleChange.bind(this);
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
          comments: data.comments,
          url: data.url,
        });
      })
      .catch((error) => console.log(error));
  }

  handleChange(event) {
    this.setState({ commentBox: event.target.value });
  }

  updateDatabase(event) {
    const { url, commentBox, comments } = this.state;
    const oldComments = comments;

    // call the post api for comments
    fetch(url, {
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      method: 'post',
      body: JSON.stringify({ text: commentBox }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          comments: [...oldComments, data],
          commentBox: '',
        });
      })
      .catch((error) => console.log(error));
    event.preventDefault();
  }

  render() {
    // This line automatically assigns this.state.numLikes to the const variable numLikes
    const { comments, commentBox } = this.state;
    // use map to create fancy list
    const commentItems = comments.map((comment) => (
      <p key={comment.commentid}>
        <a href={comment.owner_show_url}>
          {comment.owner}
        </a>
        {comment.text}
        <br />
      </p>
    ));

    // Render number of likes
    return (
      <div className="comments">
        {commentItems}
        <form className="comment-form" onSubmit={this.updateDatabase}>
          <input type="text" value={commentBox} onChange={this.handleChange} />
        </form>
      </div>
    );
  }
}

Comments.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Comments;
