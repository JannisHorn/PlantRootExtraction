/*Copyright (C) 2019 Jannis Horn - All Rights Reserved
 *You may use, distribute and modify this code under the
 *terms of the GNU GENERAL PUBLIC LICENSE Version 3.
 */

#ifndef XML_UTILS_H__
#define XML_UTILS_H__

#include <string>
#include <sstream>
#include <vector>

namespace utils {
namespace xml {

struct Attribute
{
  Attribute( const std::string& n_name, const std::string& n_val )
    : name( n_name ), val( n_val ) {}

  std::string toString()
  {
    std::stringstream sstr;
    sstr << name << "=";
    sstr << "\"" << val << "\"";
    return sstr.str();
  }

  std::string name;
  std::string val;
};

struct Element
{
  Element( const std::string& n_name, const size_t n_offset=0 ) : m_name( n_name ), m_offset( n_offset ) {}
  ~Element()
  {
    for( size_t it=0; it < m_elements.size() ; ++it )
      delete m_elements[it];
  }

  Attribute* addAttribute( const std::string& n_name, const std::string& n_val )
  {
    m_attributes.push_back( Attribute( n_name, n_val ) );
    return &(m_attributes[m_attributes.size() -1]);
  }
  Element* addElement( const std::string& n_name )
  {
    m_elements.push_back( new Element( n_name ) );
    return m_elements[m_elements.size() -1];
  }
  void addElement( Element* elem_ptr )
  {
    m_elements.push_back( elem_ptr );
  }

  std::string toString( const size_t& offset=0 )
  {
    std::string offset_str( offset *2, ' ' );
    std::stringstream sstr;
    sstr << offset_str << "<" << m_name;
    for( size_t it=0; it < m_attributes.size() ; ++it )
      sstr << " " << m_attributes[it].toString();
    if( m_elements.size() == 0 )
      sstr << "/>" << std::endl;
    else {
      sstr << ">" << std::endl;
      for( size_t it=0; it < m_elements.size() ; ++it )
        sstr << m_elements[it]->toString( offset +2 );
      sstr << offset_str <<"</" << m_name << ">" << std::endl;
    }
    return sstr.str();
  }
private:
  std::string m_name;
  std::vector<Attribute> m_attributes;
  std::vector<Element*> m_elements;
  size_t m_offset;
  size_t m_id = 0;
};

class Document
{
public:
  Document() = default;
  Document( const std::string& name ) { m_root = new Element( name ); }
  ~Document() { if ( m_root != nullptr ) delete m_root; }

  Element& getRoot() { return *m_root; }
  const Element& getRoot() const { return *m_root; }
  void setRoot( const std::string name ) { m_root = new Element( name ); }

  std::string toString() const
  {
    std::stringstream sstr;
    sstr << "<?xml version=\"1.0\" ?>" << std::endl;
    if( m_root != nullptr )
      sstr << m_root->toString();
    return sstr.str();
  }
private:
  Element* m_root = nullptr;
};

}}

#endif // XML_UTILS_H__

