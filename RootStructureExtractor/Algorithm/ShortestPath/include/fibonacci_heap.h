/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef FIBONACCI_HEAP_H__
#define FIBONACCI_HEAP_H__

#include <list>
#include <vector>
#include <memory>
#include <limits>
#include <iostream>
#include <sstream>

#include "node_list.h"

namespace utils {
template<class _Tp>
class FibonacciHeap
{
private: //Private Datastructures
  struct TreeNode;
  using TreeList = utils::NodeList<TreeNode> ;
  using TreeIter = typename utils::NodeList<TreeNode>::Iterator;
  struct TreeNode
  {
    struct Node
    {
      double key;
      _Tp val;
      TreeList children;

      Node() {}
      Node( const double ikey, const _Tp& ival ) : key(ikey), val(ival) {}
      inline size_t getDegree() const { return children.size(); }
    };
    typedef std::unique_ptr<Node> NodePtr;

    TreeNode() {}
    TreeNode( const double key, const _Tp& val ) : root( Node( key, val ) ) {}
    TreeNode( const Node& node ) : root( node ) {}
    TreeNode( const TreeNode& other ) { std::cout << "USING DELETED FUNCTION" << std::endl; }
    TreeNode( Node&& node ) : root( std::move( node ) ) {}
    TreeNode( TreeNode&& other ) : root( std::move( other.root ) ) {};
    //inline void operator=( const TreeNode& other ) { root.key = other.getKey(); root.val = other.getVal(); }
    inline void swap( TreeNode& other )
    {
      double h_k = other.getKey(); _Tp h_v = other.getVal();
      other.root.key = getKey(); other.root.val = getVal();
      root.key = h_k; root.val = h_v;
    }

    inline bool operator<( const TreeNode& other ) const { return getKey() < other.getKey(); }
    inline bool operator>( const TreeNode& other ) const { return getKey() > other.getKey(); }
    inline bool operator<=( const TreeNode& other ) const { return !operator>( other ); }
    inline bool operator>=( const TreeNode& other ) const { return !operator<( other ); }
    inline bool operator==( const TreeNode& other ) const { return getKey() == other.getKey(); }
    inline bool operator!=( const TreeNode& other ) const { return !operator==(other); }

    inline void merge( TreeList& other_list, TreeIter& other )
    {
      if( other->getKey() < getKey() )
      {
        swap( *other );
        root.children.swap( other->root.children );
      }
      root.children.splice_node( root.children.end(), other_list, other );
    }
    inline void splice( TreeList& heap, TreeIter& iter )
    {
      if( iter->val().getKey() < getKey() )
      {
        double h_k = iter->val().getKey(); _Tp h_v = iter->val().getVal();
        iter->val().root.key = getKey(); iter->val().root.val = getVal();
        root.key = h_k; root.val = h_v;
      }
      root.children.splice( root.children.end(), heap, iter );
    }
    inline Node& findMin() const { return root; }
    inline void mergeSubtreeList( TreeList& other ) { other.splice( other.end(), root.children ); }
    inline _Tp getMin() const { return root.val; }
    inline size_t getDegree() const { return root.getDegree(); }
    inline double getKey() const { return root.key; }
    inline _Tp getVal() const { return root.val; }
    inline std::string toString()
    {
      std::stringstream sstr;
      sstr << "<" << root.getDegree() << ":" << root.key << "," << root.val << ": ";
      for( TreeIter iter=root.children.begin(); iter != root.children.end(); ++iter )
        sstr << iter->toString();
      sstr << ">";
      return sstr.str();
    }

    Node root;
  };

public:
  FibonacciHeap() : m_degrees( m_max_degree, nullptr ) {};
  FibonacciHeap( const _Tp input_val ) : m_degrees( m_max_degree, nullptr ) {};
  inline void insert( const double key, const _Tp& val )
  {
    m_heap.push_back( key, val );
    ++m_size;
    if( m_min_val > key )
    {
      m_min_elem = m_heap.end();
      --m_min_elem;
      m_min_val = key;
    }
  }

  inline TreeIter& findMin() { return m_min_elem; }
  inline void deleteMin()
  {
    m_degrees[m_min_elem->getDegree()] = nullptr;
    m_min_elem->mergeSubtreeList( m_heap );
    m_heap.erase( m_min_elem );
    --m_size;
  }
  inline void searchMin()
  {
    m_min_val = std::numeric_limits<double>::max();
    for( TreeIter iter = m_heap.begin(); iter != m_heap.end(); ++iter )
    {
      if( m_min_val > iter->root.key )
      {
        m_min_val = iter->root.key;
        m_min_elem = iter;
      }
    }
  }
  inline double extractMin( _Tp& output )
  {
    TreeIter& min_iter = findMin();
    double min_val = min_iter->root.key;
    output = min_iter->root.val;
    deleteMin();
    mergeSubtreesByDegree();
    searchMin();
    return min_val;
  }

  inline size_t getSize() const { return m_size; }
  inline bool isEmpty() const { return m_heap.empty(); }

private:
  inline void mergeSubtreesByDegree()
  {
    bool still_merging = true;
    while( still_merging )
    {
      still_merging = false;
      TreeIter iter = m_heap.begin();
      while( iter != m_heap.end() )
      {
        const size_t degree = iter->getDegree();
        TreeNode* val_ptr = &(*iter);
        if( m_degrees[degree] == nullptr || m_degrees[degree] == val_ptr )
        {
          m_degrees[degree] = &(*iter);
          ++iter;
        }
        else
        {
          still_merging = true;
          TreeIter er_iter = iter;
          ++iter;
          m_degrees[degree]->merge( m_heap, er_iter );
          m_degrees[degree] = nullptr;
        }
      }
    }
  }

  TreeList m_heap;
  TreeIter m_min_elem;
  double m_min_val = std::numeric_limits<double>::max();
  size_t m_size = 0;
  const size_t m_max_degree = 256;
  std::vector<TreeNode*> m_degrees;
};
}

template <class _Tp>
inline std::ostream& operator<<( std::ostream& _ostr, const typename utils::FibonacciHeap<_Tp>::TreeNode& _obj )
{
  return _ostr << _obj.toString();
}

#endif // FIBONACCI_HEAP_H__

