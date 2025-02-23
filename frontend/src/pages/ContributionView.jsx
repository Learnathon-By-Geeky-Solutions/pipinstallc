import React from 'react';
import Navbar from '../Components/Navbar';
import { useParams } from 'react-router-dom';

function ContributionView() {
  const { id } = useParams();

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      
      {/* Breadcrumb Navigation */}
      <div className="flex items-center px-24 py-2 mt-[60px] text-sm text-purple-600 bg-gray-50">
        <button className="hover:bg-gray-100 px-3 py-1 rounded-md">Hide menu</button>
        <span className="mx-2">›</span>
        <span>DSA</span>
        <span className="mx-2">›</span>
        <span>Week 1</span>
        <span className="mx-2">›</span>
        <span>Welcome to DSA!</span>
      </div>

      {/* Main Content */}
      <div className="flex">
        {/* Left Sidebar */}
        <div className="w-72 border-r border-gray-200 p-4 h-[calc(100vh-100px)] overflow-y-auto">
          <div className="mb-6">
            <h3 className="font-medium mb-3">Overview of DSA</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm p-2 bg-blue-50 rounded">
                <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span>Welcome to DSA!</span>
                <span className="ml-auto text-gray-500">2 min</span>
              </div>
              {/* More sidebar items */}
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 p-6">
          <div className="max-w-4xl mx-auto">
            {/* Video Player Section */}
            <div className="relative bg-black aspect-video mb-6 rounded-lg overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-center">
                <img 
                  src="/path-to-thumbnail.jpg" 
                  alt="Video thumbnail" 
                  className="w-full h-full object-cover"
                />
              </div>
              {/* Video Controls */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 p-4">
                <div className="flex items-center gap-4 text-white">
                  <button className="hover:bg-white/20 p-2 rounded-full">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </button>
                  <div className="flex-1">
                    <div className="h-1 bg-white/30 rounded-full">
                      <div className="h-full w-1/3 bg-white rounded-full"></div>
                    </div>
                  </div>
                  <span>0:00 / 2:44</span>
                </div>
              </div>
            </div>

            {/* Content Tabs */}
            <div className="border-b border-gray-200">
              <nav className="flex gap-6">
                <button className="px-4 py-2 text-purple-600 border-b-2 border-purple-600">
                  Transcript
                </button>
                <button className="px-4 py-2 text-gray-500 hover:text-purple-600">
                  Notes
                </button>
                <button className="px-4 py-2 text-gray-500 hover:text-purple-600">
                  Downloads
                </button>
              </nav>
            </div>

            {/* Transcript Content */}
            <div className="mt-6 space-y-4">
              <div className="flex gap-4">
                <span className="text-gray-500 w-12">0:01</span>
                <p className="flex-1">
                  Welcome to Data Structures and Algorithms. What is DSA? You probably use it many times a day without even knowing it...
                </p>
              </div>
              {/* More transcript items */}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContributionView; 