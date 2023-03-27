/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef NODE_LIST_BU_H__
#define NODE_LIST_BU_H__

#include <string>
#include <sstream>
#include <memory>

namespace utils
{

template<class _Tp>
class NodeList
{
public:

  class NodeBase // TODO use (smart-)Pointer to store data -> allow for easier access etc.
  {
  public:
    NodeBase() = default;
    virtual ~NodeBase() {}
    //TODO allow for direct in position construction

    inline void concatNeighbors()
    {
      if( pred() != nullptr )
        pred()->setSucc( succ() );
      if( succ() != nullptr )
        succ()->setPred( pred() );
    }

    inline void setPred( NodeBase& n_pred ) { m_pred = &n_pred; }
    inline void setPred( NodeBase* n_pred ) { m_pred = n_pred; }
    inline NodeBase* pred() const { return m_pred; }
    inline void setSucc( NodeBase& n_succ ) { m_succ = &n_succ; }
    inline void setSucc( NodeBase* n_succ ) { m_succ = n_succ; }
    inline NodeBase* succ() const { return m_succ; }
    inline NodeBase* operator++() const { return succ(); }
    inline NodeBase* operator--() const { return pred(); }

    virtual inline void setValue( const _Tp& n_val ) {}
    virtual inline void setValue( _Tp&& n_val ) {}
    virtual inline _Tp& val() {}
    virtual inline const _Tp& val() const {}

    virtual inline bool operator<( const NodeBase& other ) const { return false; }
    virtual inline bool operator>( const NodeBase& other ) const { return false; }
    virtual inline bool operator<=( const NodeBase& other ) const { return false; }
    virtual inline bool operator>=( const NodeBase& other ) const { return false; }
    virtual inline bool operator==( const NodeBase& other ) const { return false; }
    virtual inline bool operator!=( const NodeBase& other ) const { return false; }

    inline std::string toString() { return ""; }
  protected:
    NodeBase* m_pred=nullptr;
    NodeBase* m_succ=nullptr;
  };

  class Node : public NodeBase
  {
  public:
    Node() = default;
    Node( const _Tp& n_val ) : m_val( n_val ) {}
    Node( _Tp&& n_val ) { m_val = std::move( n_val ); }
    template<typename... _Ts> Node( _Ts... args ) : m_val( _Tp( args... ) ) {}

    inline void setValue( const _Tp& n_val ) override { new (&m_val) _Tp( n_val ); }
    inline void setValue( _Tp&& n_val ) override { new (&m_val) _Tp( std::move( n_val ) ); }
    inline _Tp& val() override { return m_val; }
    inline const _Tp& val() const override { return m_val; }
    inline void switchContent( Node& other )
    {
      const _Tp o_val = other.val;
      other.setVal( m_val );
      setVal( o_val );
    }

    inline bool operator<( const NodeBase& other ) const override { return m_val < other.val(); }
    inline bool operator>( const NodeBase& other ) const override { return m_val > other.val(); }
    inline bool operator<=( const NodeBase& other ) const override { return !operator>( other ); }
    inline bool operator>=( const NodeBase& other ) const override { return !operator<( other ); }
    inline bool operator==( const NodeBase& other ) const override { return m_val == other.val(); }
    inline bool operator!=( const NodeBase& other ) const override { return !operator==(other); }

    inline std::string toString() { std::stringstream sstr; sstr << m_val.toString(); return sstr.str(); }
  private:
    _Tp m_val;
  };

  struct Iterator
  {
    Iterator() : ptr( nullptr ) {}
    Iterator( NodeBase* n_ptr ) : ptr( n_ptr ) {}
    inline void operator++() { ptr=ptr->succ(); }
    inline void operator--() { ptr=ptr->pred(); }
    inline _Tp& operator*() const { return reinterpret_cast<Node*>( ptr )->val(); }
    inline _Tp* operator->() const { return &(reinterpret_cast<Node*>( ptr )->val()); } // TODO rework for easier access without constant val() calls

    inline void operator=( const Node* node ) const { ptr = node; }
    inline bool operator==( const Iterator& other ) const { return ptr == other.getPtr(); }
    inline bool operator!=( const Iterator& other ) const { return !operator==(other); }

    inline NodeBase* getPtr() { return ptr; }
    inline NodeBase* getPtr() const { return ptr; }
    inline Node* getNodePtr() { return reinterpret_cast<Node*>( ptr ); }
    inline Node* getNodePtr() const { return reinterpret_cast<Node*>( ptr ); }
    inline NodeBase* pred() const { return ptr->pred(); }
    inline NodeBase* succ() const { return ptr->succ(); }

    NodeBase* ptr;
  };


  NodeList() { createEnd(); }
  NodeList( NodeList&& other )
  {
    Iterator end_elem = other.end().pred();
    m_head = other.m_head;
    m_tail = other.m_tail;
    m_size = other.m_size;
    other.m_head = nullptr;
    other.m_tail = nullptr;
  }
  ~NodeList() { clear(); delete m_tail; }
  inline size_t size() const { return m_size; }
  inline bool empty() const { return m_head == m_tail; }
  inline Iterator begin() const { return Iterator( m_head ); }
  inline Iterator end() const { return Iterator( m_tail ); }
  inline NodeBase* begin_ptr() const { return m_head; }
  inline NodeBase* end_ptr() const { return m_tail; }
  inline void setHead( NodeBase* new_head ) { m_head = new_head; }
  inline void setHead( const Iterator& new_head ) { m_head = new_head.getPtr(); }
  inline void _swap( NodeList& other )
  {
    m_head = other.begin_ptr();
    m_tail = other.end_ptr();
    m_size = other.size();
  }
  inline void swap( NodeList& other )
  {
    NodeBase* h_begin = other.begin_ptr();
    NodeBase* h_end = other.end_ptr();
    size_t h_size = other.size();
    other._swap( *this );
    m_head = h_begin;
    m_tail = h_end;
    m_size = h_size;
  }
  /*inline void operator=( NodeList& other )
  {
    createEnd();
    Iterator end_elem = other.end().pred();
    m_head = other.begin();
    concat( end_elem, m_tail );
    other.disconnect_node( other.begin(), other.end() );
  }*/

  inline void clear()
  {
    Iterator iter=begin();
    while( iter != end() )
    {
      Node* last_ptr = iter.getNodePtr();
      ++iter;
      delete last_ptr;
    }
    m_size = 0;
  }
  inline void reset()
  {
    m_head = m_tail;
    m_tail.setPred( nullptr );
    m_size = 0;
  }
  inline void insert( const _Tp& n_val, Iterator iter )
  {
    Node* n_node = new Node( n_val );
    _insert( n_node, iter );
  }
  template<class... _Ts> inline void insert( Iterator iter, const _Ts... args )
  {
    Node* n_node = new Node( args... );
    _insert( n_node, iter );
  }
  inline void erase( const Iterator& elem )
  {
    if( elem == begin() )
      pop_front();
    else
    {
      deleteNode( elem );
      --m_size;
    }
  }
  inline void erase( const Node* elem ) { erase( Iterator( elem ) ); }
  inline void disconnect_node( const Iterator& iter ) { concat( iter.pred(), iter.succ() ); }
  inline void disconnect_node( const Iterator& s_iter, const Iterator& e_iter ) { concat( s_iter, e_iter.pred() ); }
  inline void push_back( const _Tp& n_val )
  {
    Node* n_node = new Node( n_val );
    _push_back( n_node );
  }
  inline void push_back( _Tp&& n_val )
  {
    Node* n_node = new Node();
    n_node->setValue( std::move( n_val ) );
    _push_back( n_node );
  }
  template<class... _Ts> inline void push_back( const _Ts... args )
  {
    Node* n_node = new Node( args... );
    _push_back( n_node );
  }
  inline void pop_back()
  {
    Node* node = reinterpret_cast<Node*>( end().pred() );
    concat( node->pred(), end() );
    delete node;
    --m_size;
  }
  inline void push_front( const _Tp& n_val )
  {
    Node* n_node = new Node( n_val );
    _push_front( n_val );
  }
  template<class... _Ts> inline void push_front( const _Ts... args )
  {
    Node* n_node = new Node( args... );
    _push_front( n_node );
  }
  inline void pop_front()
  {
    NodeBase* node = begin().succ();
    delete begin().getNodePtr();
    m_head = node;
    m_head->setPred( nullptr );
    --m_size;
  }

  inline void extract( const Iterator& iter )
  {
    if( iter == begin() )
    {
      setHead( iter.succ() );
      iter.getPtr()->setPred( nullptr );
    }
    else
      concat( iter.pred(), iter.succ() );
    --m_size;
  }

  inline void splice_node( const Iterator& iter, NodeList& other, const Iterator& o_node )
  {
    other.extract( o_node );
    if( iter == begin() )
    {
      o_node.getPtr()->setPred( nullptr );
      concat( o_node, m_head );
      m_head = o_node.getPtr();
    }
    else
    {
      NodeBase* this_pred = iter.pred();
      concat( o_node, iter );
      concat( this_pred, o_node );
    }
    ++m_size;
  }

  inline void splice( const Iterator& iter, NodeList& other, const Iterator& o_start, const Iterator& o_end )
  {
    Node* this_succ = iter.succ();
    if( o_start == other.begin() )
      other.begin() = o_end;
    else
      other.concat( o_start.pred(), o_end() );
    concat( iter, o_start );
    concat( o_end.pred(), this_succ );
  }

  inline void splice( const Iterator& iter, NodeList& other, const Iterator& o_start ) { splice( iter, other, o_start, other.end() ); }

  inline void splice( const Iterator& iter, NodeList& other )
  {
    NodeBase* this_pred = iter.pred();
    concat( this_pred, other.begin() );
    concat( other.end().pred(), iter );
    m_size += other.size();
    other.setHead( other.end() );
    other.end().getPtr()->setPred( nullptr );
  }

  inline void splice( const Iterator& iter, NodeList&& other, const Iterator& o_start, const Iterator& o_end )
  {
    Node* this_succ = iter.succ();
    if( o_start == other.begin() )
      other.m_head = o_end;
    else
      other.concat( o_start.pred(), o_end() );
    concat( iter, o_start );
    concat( o_end--, this_succ );
  }

  inline void splice( const Iterator& iter, NodeList&& other, const Iterator& o_start ) { splice( iter, other, o_start, other.end() ); }
  inline void splice( const Iterator& iter, NodeList&& other ) { splice( iter, other, other.begin(), other.end() ); }

  inline std::string toString()
  {
    Iterator iter = begin();
    std::stringstream sstr;
    while( iter != end() )
    {
      sstr << iter->toString() << " - ";
      ++iter;
    }
    return sstr.str();
  }

private:
  inline void createEnd()
  {
    NodeBase* node = new NodeBase();
    m_tail = node;
    m_head = node;
  }
  inline void concat( Iterator& iter, NodeBase* n_node ) const
  {
    iter.succ()->setPred( n_node );
    iter->setSucc( n_node );
  }
  inline void concat( NodeBase* n_node, Iterator& iter ) const
  {
    n_node.succ()->setPred( iter );
    n_node->setSucc( iter );
  }
  inline void concatInv( Iterator& iter, NodeBase* n_node ) const
  {
    iter.pred()->setSucc( n_node );
    iter->setPred( n_node );
  }
  inline void concat( NodeBase* n1, NodeBase* n2 ) const
  {
    n1->setSucc( n2 );
    n2->setPred( n1 );
  }
  inline void concat( const Iterator& iter1, const Iterator& iter2 ) const { concat( iter1.getPtr(), iter2.getPtr() ); }

  inline void addFirstElement( Node* n_node )
  {
    m_head = n_node;
    concat( n_node, m_tail );
  }
  inline void deleteNode( const Iterator& iter ) { deleteNode( iter.getNodePtr() ); }
  inline void deleteNode( Node* node )
  {
    node->concatNeighbors();
    delete node;
  }

  inline void _insert( Node* n_node, const Iterator& iter )
  {
    if( empty() )
      addFirstElement( n_node );
    else
    {
      NodeBase* iter_pred = iter.pred();
      concat( n_node, iter );
      if( iter == begin() )
        m_head = n_node;
      else
        concat( iter_pred, n_node );
    }
    ++m_size;
  }
  inline void _push_back( Node *n_node )
  {
    if( empty() )
      addFirstElement( n_node );
    else
    {
      concat( m_tail->pred(), n_node );
      concat( n_node, m_tail );
    }
    ++m_size;
  }
  inline void _push_front( Node *n_node )
  {
    if( empty() )
      addFirstElement( n_node );
    else
    {
      concat( n_node, begin() );
      m_head = n_node;
    }
    ++m_size;
  }

  NodeBase* m_head=nullptr;
  NodeBase* m_tail=nullptr;
  size_t m_size = 0;
};

}
#endif // NODE_LIST_H__
