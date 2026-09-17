export const getDomains = async (req, res) => {
  const domains = [
    {
      id: 'Web Development',
      title: 'Web Development',
      description: 'Frontend, Backend, and Full-Stack web architecture & frameworks.',
      icon: 'Globe',
      popularBadge: true,
    },
    {
      id: 'AI/ML',
      title: 'AI/ML',
      description: 'Machine Learning, Neural Networks, NLP, and Generative AI systems.',
      icon: 'Brain',
      popularBadge: true,
    },
    {
      id: 'App Development',
      title: 'App Development',
      description: 'Native & Cross-platform iOS/Android mobile applications.',
      icon: 'Smartphone',
      popularBadge: false,
    },
    {
      id: 'Cybersecurity',
      title: 'Cybersecurity',
      description: 'Network security, ethical hacking, cryptography & audit compliance.',
      icon: 'ShieldAlert',
      popularBadge: false,
    },
    {
      id: 'Cloud Computing',
      title: 'Cloud Computing',
      description: 'AWS, GCP, Azure, DevOps pipelines, Kubernetes & infrastructure.',
      icon: 'Cloud',
      popularBadge: false,
    },
    {
      id: 'Core Software Engineering / DSA',
      title: 'Core Software Engineering / DSA',
      description: 'Data Structures, Algorithms, Low-Level System Design, and C++/Java.',
      icon: 'Terminal',
      popularBadge: false,
    },
  ];

  return res.status(200).json(domains);
};
