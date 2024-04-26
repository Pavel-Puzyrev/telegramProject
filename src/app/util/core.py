def get_month_list(m_start, m_end):
    if not (0 < m_start < 13 and 0 < m_end < 13):
        print("out of range")
        return None
    elif m_start <= m_end:
        return [x for x in range(m_start, m_end + 1)]
    else:
        return list(range(m_start, 13)) + list(range(1, m_end + 1))
