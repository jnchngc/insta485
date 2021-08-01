import React from 'react';
import moment from 'moment';
import PropTypes from 'prop-types';
import Likes from './likes';
import Comments from './comments';

class Post extends React.Component {
  /* Display post information for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.likeRef = React.createRef();
    const { url } = this.props;
    const urlArg = url;
    this.state = {
      age: '',
      imgUrl: '',
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
      url: urlArg,
    };
    this.handleDoubleClick = this.handleDoubleClick.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get post information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          age: data.age,
          imgUrl: data.img_url,
          owner: data.owner,
          ownerImgUrl: data.owner_img_url,
          ownerShowUrl: data.owner_show_url,
          postShowUrl: data.post_show_url,
          url: data.url,
        });
      })
      .catch((error) => console.log(error));
  }

  handleDoubleClick() {
    this.likeRef.current.updateLikesOnDoubleClick();
  }

  render() {
    const {
      age, imgUrl, owner, ownerImgUrl, ownerShowUrl, postShowUrl, url,
    } = this.state;
    const humanReadableAge = moment.utc(age).fromNow();
    const likesUrl = `${url}likes/`;
    const commentsUrl = `${url}comments/`;
    // Render individual post
    return (
      <div className="entirePost">
        <div className="postTop">
          <a className="profilePic" href={ownerShowUrl}>
            <img src={ownerImgUrl} alt="profilePicture" height="25" width="25" />
          </a>
          <a href={ownerShowUrl}>
            {owner}
          </a>
          <div className="timestamp">
            <a href={postShowUrl}>
              {humanReadableAge}
            </a>
          </div>
        </div>
        <img className="picture" src={imgUrl} alt="" onDoubleClick={this.handleDoubleClick} />
        <Likes url={likesUrl} ref={this.likeRef} />
        <Comments url={commentsUrl} />
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;
