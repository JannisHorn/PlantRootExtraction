/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef HASH_TABLE_H__
#define HASH_TABLE_H__

#include <array>
#include <vector>
#include <memory>
#include <sstream>

namespace utils
{
template<class _Tp>
class HashTable
{
public:
  using HashBucket = std::unique_ptr<std::vector<_Tp>>;

  HashTable( const size_t& width ) : HashTable( width, nullptr ) {}
  HashTable( const size_t& width, size_t (*hash_func)( const _Tp& ) ) : m_hash_func( hash_func ), m_width( width )
  {
    for( size_t it=0; it < m_width ; ++it )
      m_hash_table.push_back( HashBucket( new std::vector<_Tp>() ) );
  }

  inline void setHashFunc( size_t (*hash_func)( const _Tp& ) ) { m_hash_func = hash_func(); }
  inline size_t hashVal( const _Tp& val ) const { return m_hash_func( val ); }

  inline void clear() { for( size_t it=0; it < m_width; ++it ) m_hash_table[it]->clear(); }

  inline size_t size() const { return m_size; }

  inline void insert( const _Tp& n_val ) { insert( n_val, m_hash_func( n_val ) ); }
  inline void insert( const _Tp& n_val, const size_t& key ) { m_hash_table[key]->push_back(  n_val ); ++m_size; }

  inline bool contains( const _Tp& val ) const { return contains( val, m_hash_func( val ) ); }
  inline bool contains( const _Tp& val, const size_t& key ) const { return !( find( val, key ) == nullptr ); }

  inline _Tp* find( const _Tp& val ) { find( val, m_hash_func( val ) ); }
  inline _Tp* find( const _Tp& val, const size_t& key )
  {
    HashBucket& curr_bucket = m_hash_table[key];
    for( size_t it=0; it < curr_bucket->size() ; ++it )
      if( (*curr_bucket)[it] == val ) return &((*curr_bucket)[it]);
    return nullptr;
  }
  inline const _Tp* find( const _Tp& val ) const { return find( val, m_hash_func( val ) ); }
  inline const _Tp* find( const _Tp& val, const size_t key ) const { return find( val, key ); }

  inline HashBucket& getKey( const size_t& key ) { return m_hash_table[key]; }
  inline const HashBucket& getKey( const size_t& key ) const { return m_hash_table[key]; }

  inline std::string toString() const
  {
    std::stringstream sstr;
    for( size_t it=0; it < m_width ; ++it )
      sstr << toString( m_hash_table[it] ) << std::endl;
    return sstr.str();
  }

  inline std::string toString( const HashBucket& hsb ) const
  {
    std::stringstream sstr;
    sstr << "<";
    for( size_t it=0; it < hsb->size() ; ++it )
      sstr << (*hsb)[it] << ", ";
    sstr << ">";
    return sstr.str();
  }

private:
  void recompSize()
  {
    m_size = 0;
    for( size_t it=0; it < m_width ; ++it )
      m_size += m_hash_table[it]->size();
  }

  size_t (*m_hash_func)( const _Tp& ) = nullptr;
  std::vector<HashBucket> m_hash_table;
  size_t m_size = 0;
  const size_t m_width;
};
}

#endif // HASH_TABLE_H__

