/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef GRAPH_H__
#define GRAPH_H__

#include <vector>
#include <sstream>
#include <iostream>

namespace utils
{
template<class _Tp>
class GridTree
{
public:
  class Node; class Branch;

  typedef Node* NodePtr;
  typedef std::vector<Node*> NodeVector;
  typedef std::vector<Branch> BranchVector;

  class Node
  {
  public:
    Node() {}
    Node( const Node& other ) : m_val( other.getVal() ) {}
    template<typename... _Ts> Node( _Ts... args )
      : m_val( _Tp( args... ) ), m_pred( nullptr ) {}
    template<typename... _Ts> Node( const Node* pred, _Ts... args )
      : m_val( _Tp( args... ) ), m_pred( const_cast<Node*>( pred ) ) {}
    template<typename... _Ts> Node( Node* pred, _Ts... args )
      : m_val( _Tp( args... ) ), m_pred( pred ) {}
    ~Node() { for( size_t it=0; it < m_childs.size() ; ++it ) delete m_childs[it]; }

    inline Node operator=( Node* other )
    {
      setVal( other.getVal() );
    }

    inline void setVal( const _Tp& other ) { m_val = other; }
    inline _Tp& getVal() { return m_val; }
    inline const _Tp& getVal() const { return m_val; }
    inline bool isLeaf() const { return m_childs.empty(); }

    inline const NodeVector& getChilds() const { return m_childs; }
    inline const NodeVector& getChilds() { return m_childs; }
    inline const NodePtr& getChild( const int& it ) const { return m_childs[it]; }
    inline const NodePtr& getChild( const int& it ) { return m_childs[it]; }
    inline void disconnect() { m_childs = NodeVector(); }
    inline size_t rank() const { return m_childs.size(); }
    inline void deleteChild( const int& it )
    {
      delete m_childs[it];
      m_childs.erase( m_childs.begin()+it );
    }

    inline size_t size() const
    {
      size_t sum = 0;
      for( size_t c_it=0; c_it < rank() ; ++c_it )
        sum += m_childs[c_it]->size();
      return ( sum +rank() );
    }

    inline void setPred( Node* pred ) { m_pred = pred; }
    inline Node* getPred() const { return m_pred; }

    inline Node* insert( Node* other )
    {
      m_childs.push_back( other );
      return m_childs[m_childs.size()-1];
    }
    template<typename... _Ts>
    inline Node* insert( const _Ts... args )
    {
      m_childs.push_back( new Node( args... ) );
      return m_childs[m_childs.size()-1];
    }

    inline void replace( Node* other, const size_t& it )
    {
      m_childs[it] = other;
      other->setPred( this );
    }

    inline void getLeafs( NodeVector& leafs )
    {
      if( isLeaf() ) leafs.push_back( this );
      else for( size_t it=0; it < m_childs.size() ; ++it ) m_childs[it]->getLeafs( leafs );
    }

    inline void repairPreds( Node* pred )
    {
      m_pred = pred;
      for( size_t c_it=0; c_it < rank() ; ++c_it )
        m_childs[c_it]->repairPreds( this );
    }

  protected:
    _Tp m_val;
    Node* m_pred = nullptr;
    NodeVector m_childs;
  };




  class Branch
  {
  public:
    Branch( const Node* leaf )
    {
      m_size = 1;
      Node* curr_node = const_cast<Node*>( leaf ), *pred_node = leaf->getPred();
      m_tail = const_cast<Node*>( leaf );
      while( pred_node != nullptr )
      {
        if( pred_node->rank() > 1 )
          break;
        curr_node = pred_node;
        pred_node = curr_node->getPred();
        ++m_size;
      }
      if( pred_node != nullptr )
      {
        ++m_size;
        m_root = pred_node;
        for( size_t it=0; it < m_root->rank() ; ++it )
          if( m_root->getChilds()[it] == curr_node )
            m_root_it = it;
      }
      else
        m_root = curr_node;
      m_iter = m_root;
    }

    inline NodePtr next()
    {
      return next( m_tail );
    }

    inline NodePtr next( const NodePtr& target )
    {
      if( m_iter != target )
      {
        m_iter = m_iter->getChilds()[0];
        return m_iter;
      }
      else return nullptr;
    }

    inline void deleteIter() // Very expensive -> only set pointer once!
    {
      if( m_iter == m_tail )
        throw std::runtime_error( "Tried to delete tail of Graph::Branch!" );
      if( m_iter == m_root )
        throw std::runtime_error( "Tried to delete root of Graph::Branch!" );
      else
      {
        Node* pred = m_iter->getPred();
        Node* next = m_iter->getChilds()[0];
        if( pred == m_root )
          pred->replace( next, m_root_it );
        else
          pred->replace( next, 0 );
        m_iter->disconnect();
        delete m_iter;
        m_iter = next;
      }
    }

    inline void deleteSegment( const NodePtr& start, const NodePtr& target )
    {
      m_iter = start;
      while( m_iter != target )
        deleteIter();
    }

    inline void deleteLeafBranch()
    {
      m_root->deleteChild( m_root_it );
    }

    inline NodePtr getRoot() const { return m_root; }
    inline NodePtr getTail() const { return m_tail; }
    inline NodePtr getIter() const { return m_iter; }
    inline NodePtr getStart() const { return m_root->getChilds()[m_root_it]; }
    inline size_t size() const { return m_size; }
    inline void setIter( const NodePtr& pos ) { m_iter = pos; }
    inline size_t getRootIt() const { return m_root_it; }

  protected:
    NodePtr m_tail;
    NodePtr m_root;
    NodePtr m_iter;
    size_t m_size;
    size_t m_root_it = 0;
  };




public:
  GridTree() {}
  template<typename... _Ts> GridTree( const _Ts... args ) : m_root( args... ) {};
  GridTree( const NodePtr node ) : m_root( node ) {};
  GridTree( const GridTree& other ) : m_root( new Node( other.getRoot()->getVal() ) ) { append( m_root, other.getRoot() ); }
  ~GridTree() { clear(); }

  inline void append( Node* this_node, const Node* other )
  {
    for( size_t it=0; it < other->rank() ; ++it )
    {
      NodePtr new_node = insert( this_node, other->getChilds()[it]->getVal() );
      append( new_node, other->getChilds()[it] );
    }
  }

  inline void clear() { if( !empty() ) delete m_root; }

  inline bool empty() const { return m_root == nullptr; }

  inline size_t size() const { return m_root->size(); }

  template<typename... _Ts>
  inline NodePtr insert( const NodePtr pos, const _Ts... args ) { return pos->insert( pos, args... ); }
  template<typename... _Ts>
  inline NodePtr insert( const _Ts... args ) { if( empty() ) m_root = new Node( args... ); return nullptr; }

  inline void deleteNode( const NodePtr& node )
  {
    NodeVector& childs = node->getChilds();
    NodePtr pred = node->getPred();
    for( size_t it=0; it < childs.size() ; ++it )
      pred->insert( childs[it] );
    node->disconnect();
    delete node;
  }

  inline NodePtr getRoot() const { return m_root; }
  inline NodePtr getRoot() { return m_root; }
  inline void setRoot( Node* root ) { m_root = root; }
  inline void getLeafs( NodeVector& leafs_out ) const
  {
    leafs_out = NodeVector();
    m_root->getLeafs( leafs_out );
  }
  inline void getBranches( BranchVector& out ) const
  {
    Node* curr_node = m_root;
    for( size_t it=0; it < curr_node->rank() ; ++it )
      addBranch( curr_node->getChilds()[it], out );
  }

  inline void repairPreds()
  {
    m_root->repairPreds( nullptr );
  }
protected:
  inline void addBranch( const Node* curr_node, BranchVector& out ) const
  {
    //std::cout << "addBranch" << curr_node->rank() << std::endl;
    if( curr_node->rank() == 1 )
      addBranch( curr_node->getChilds()[0], out );
    else if( curr_node->rank() == 0 )
      out.push_back( Branch( curr_node ) );
    else if( curr_node->rank() > 1 )
    {
      out.push_back( Branch( curr_node ) );
      for( size_t it=0; it < curr_node->rank() ; ++it )
        addBranch( curr_node->getChilds()[it], out );
    }
  }

  Node* m_root = nullptr;
};

template<class _Tp> inline GridTree<_Tp>* CreateNewTreePtr() { return new GridTree<_Tp>(); }

}

#endif // GRAPH_H__

