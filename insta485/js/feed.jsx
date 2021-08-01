import React from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';
import PropTypes from 'prop-types';
import Post from './post';

class Feed extends React.Component {
  /* Display post information for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    const { url } = this.props;
    this.state = {
      next: `${url}?page=1`,
      results: [],
      nextCount: 0,
      url: `${url}`,
    };

    // binding lets us call member functions in returned html
    this.getNextPosts = this.getNextPosts.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.state;

    // Call REST API to get 10 newest post information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          next: data.next,
          results: data.results,
          nextCount: data.next.length,
          url: data.url,
        });
      })
      .catch((error) => console.log(error));
  }

  getNextPosts() {
    // call api to get next 10 posts when user scrolls to the bottom of the page
    const { next, results } = this.state;
    // Call REST API to get 10 newest post information
    fetch(next, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          next: data.next,
          results: results.concat(data.results),
          nextCount: data.next.length,
          url: data.url,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // assign variables for html
    const { results, nextCount } = this.state;

    // use map to create fancy list
    const posts = results.map((post) => (
      <div key={post.postid}>
        <Post url={post.url} />
      </div>
    ));

    // Render individual post
    return (
      // return html for list of posts
      <div className="allPosts">
        <InfiniteScroll
          dataLength={posts.length}
          next={this.getNextPosts}
          hasMore={nextCount}
          loader={<h4>Loading...</h4>}
          endMessage={(
            <p style={{ textAlign: 'center' }}>
              <b>Yay! You have seen it all</b>
            </p>
          )}
        >
          {posts}
        </InfiniteScroll>
      </div>
    );
  }
}

Feed.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Feed;
